from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg, Count, Sum
from django.shortcuts import render

from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .filters import RecetaFilter
from .models import Auditoria, Categoria, Favorito, Ingrediente, HistorialReceta, Receta, Valoracion
from .permissions import IsCookOrAdmin, OwnResourcePermission, RecipePermission
from .serializers import CategoriaSerializer, FavoritoSerializer, IngredienteSerializer, RecetaSerializer, ValoracionSerializer


TRANSITIONS = {
    Receta.Estado.BORRADOR: Receta.Estado.REVISION,
    Receta.Estado.REVISION: Receta.Estado.PUBLICADA,
    Receta.Estado.PUBLICADA: Receta.Estado.ARCHIVADA,
    Receta.Estado.ARCHIVADA: Receta.Estado.BORRADOR,
}


def transition_recipe(recipe, target, user, detail=""):
    expected = TRANSITIONS.get(recipe.estado)
    if expected != target:
        raise ValueError(f"Transición inválida: {recipe.estado} -> {target}.")
    previous = recipe.estado
    recipe.estado = target
    recipe.save(update_fields=["estado", "updated_at"])
    HistorialReceta.objects.create(
        receta=recipe,
        usuario=user,
        accion="CAMBIO_ESTADO",
        estado_anterior=previous,
        estado_nuevo=target,
        detalle=detail,
    )
    Auditoria.objects.create(
        usuario=user,
        accion="CAMBIO_ESTADO_RECETA",
        modelo=Receta._meta.label,
        objeto_id=recipe.pk,
        detalle={"estado_anterior": previous, "estado_nuevo": target},
    )
    return recipe


def api_home(request):
    """Render an HTML page with main API endpoints and examples."""
    base = request.build_absolute_uri('/')[:-1]
    context = {
        "endpoints": {
            "recetas": f"{base}/api/recetas/",
            "ingredientes": f"{base}/api/ingredientes/",
            "categorias": f"{base}/api/categorias/",
            "valoraciones": f"{base}/api/valoraciones/",
            "favoritos": f"{base}/api/favoritos/",
            "token": f"{base}/api/auth/token/",
            "reportes_recetas": f"{base}/api/reportes/recetas/",
        },
        "example_create_receta": {
            "nombre": "Sopa de verduras",
            "descripcion": "Sopa casera de temporada.",
            "preparacion": "Cortar, sofreír, cubrir con agua y cocer.",
            "tiempo_preparacion": 45,
            "dificultad": "FACIL",
            "categorias": [1],
            "ingredientes_data": [
                {"ingrediente_id": 1, "cantidad": "300.000"},
                {"ingrediente_id": 2, "cantidad": "10.000"},
            ],
        },
    }
    return render(request, "api_root.html", context)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    summary="Lista y crea recetas",
    description=(
        "Lista recetas con filtros, búsqueda y ordenamiento. "
        "Permite crear recetas si se está autenticado y es Cocinero."
    ),
    parameters=[
        OpenApiParameter("nombre", OpenApiTypes.STR, description="Filtro por nombre (icontains)"),
        OpenApiParameter("categoria", OpenApiTypes.STR, description="Filtro por nombre de categoría (iexact)"),
        OpenApiParameter("cocinero", OpenApiTypes.INT, description="ID del cocinero"),
        OpenApiParameter("dificultad", OpenApiTypes.STR, description="FACIL|MEDIA|DIFICIL"),
        OpenApiParameter("estado", OpenApiTypes.STR, description="BORRADOR|REVISION|PUBLICADA|ARCHIVADA"),
        OpenApiParameter("tiempo_maximo", OpenApiTypes.INT, description="Tiempo de preparación máximo (<=)"),
        OpenApiParameter("ingrediente", OpenApiTypes.STR, description="Filtrar por ingrediente (nombre)"),
        OpenApiParameter("search", OpenApiTypes.STR, description="Búsqueda full-text (nombre, descripcion)"),
        OpenApiParameter("ordering", OpenApiTypes.STR, description="Campos para ordenar: created_at, nombre, total_valoraciones, promedio_puntuacion"),
    ],
    responses={200: RecetaSerializer(many=True)},
)
class RecetaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Receta con filtros, búsqueda, ordenamiento,
    paginación y transiciones transaccionales de estado.
    """
    serializer_class = RecetaSerializer
    # Permitir lectura pública y requerir autenticación para operaciones de escritura
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecetaFilter
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["created_at", "nombre", "total_valoraciones", "promedio_puntuacion"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = Receta.objects.select_related("cocinero").prefetch_related("categorias", "ingredientes_receta__ingrediente")
        queryset = queryset.annotate(total_valoraciones=Count("valoraciones", distinct=True), promedio_puntuacion=Avg("valoraciones__puntuacion"))
        if user.is_staff or user.is_superuser or user.groups.filter(name="Administrador").exists():
            return queryset
        if user.groups.filter(name="Cocinero").exists():
            return queryset.filter(estado=Receta.Estado.PUBLICADA) | queryset.filter(cocinero=user)
        return queryset.filter(estado=Receta.Estado.PUBLICADA)

    def perform_create(self, serializer):
        serializer.save(cocinero=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        target = request.data.get("estado")
        previous = instance.estado
        data = request.data.copy()
        data.pop("estado", None)
        with transaction.atomic():
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if target is not None and target != previous:
                try:
                    transition_recipe(instance, target, request.user)
                except ValueError as exc:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({"estado": str(exc)})
        return Response(self.get_serializer(instance).data)

    def _action_transition(self, request, pk, target):
        with transaction.atomic():
            recipe = self.get_queryset().select_for_update().get(pk=pk)
            self.check_object_permissions(request, recipe)
            try:
                transition_recipe(recipe, target, request.user)
            except ValueError as exc:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"estado": str(exc)})
        return Response(self.get_serializer(recipe).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="enviar-revision")
    def enviar_revision(self, request, pk=None):
        return self._action_transition(request, pk, Receta.Estado.REVISION)

    @action(detail=True, methods=["post"])
    def publicar(self, request, pk=None):
        return self._action_transition(request, pk, Receta.Estado.PUBLICADA)

    @action(detail=True, methods=["post"])
    def archivar(self, request, pk=None):
        return self._action_transition(request, pk, Receta.Estado.ARCHIVADA)


class IngredienteViewSet(viewsets.ModelViewSet):
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteSerializer
    # Lectura pública, escritura por usuarios autenticados
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["nombre"]


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsCookOrAdmin]
    search_fields = ["nombre"]


class ValoracionViewSet(viewsets.ModelViewSet):
    serializer_class = ValoracionSerializer
    permission_classes = [OwnResourcePermission]

    def get_queryset(self):
        return Valoracion.objects.select_related("usuario", "receta").filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class FavoritoViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritoSerializer
    permission_classes = [OwnResourcePermission]

    def get_queryset(self):
        return Favorito.objects.select_related("receta").filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reporte_recetas(request):
    data = Receta.objects.values("estado").annotate(total=Count("id")).order_by("estado")
    return Response(list(data))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reporte_usuarios(request):
    data = User.objects.filter(recetas__isnull=False).annotate(total_recetas=Count("recetas", distinct=True)).values("id", "username", "total_recetas").order_by("-total_recetas")
    return Response(list(data))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reporte_ingredientes(request):
    data = Ingrediente.objects.filter(recetas_ingrediente__isnull=False).annotate(
        total_usos=Count("recetas_ingrediente", distinct=True), cantidad_total=Sum("recetas_ingrediente__cantidad")
    ).values("id", "nombre", "total_usos", "cantidad_total").order_by("-total_usos")
    return Response(list(data))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reporte_valoraciones(request):
    data = Receta.objects.filter(valoraciones__isnull=False).annotate(
        promedio=Avg("valoraciones__puntuacion"), total=Count("valoraciones", distinct=True)
    ).values("id", "nombre", "promedio", "total").order_by("-promedio", "-total")
    return Response(list(data))
