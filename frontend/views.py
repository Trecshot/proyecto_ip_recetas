import re

from django.db.models import Prefetch, Q
from django.views.generic import DetailView, ListView

from api.models import Categoria, Receta, RecetaIngrediente


def get_receta_queryset():
    return (
        Receta.objects.filter(estado=Receta.Estado.PUBLICADA)
        .select_related("cocinero")
        .prefetch_related(
            "categorias",
            Prefetch(
                "ingredientes_receta",
                queryset=RecetaIngrediente.objects.select_related("ingrediente"),
            ),
        )
    )


class RecetaListView(ListView):
    model = Receta
    template_name = "lista_recetas.html"
    context_object_name = "recetas"
    paginate_by = 6

    def get_queryset(self):
        queryset = get_receta_queryset()
        query = self.request.GET.get("q", "").strip()
        categoria = self.request.GET.get("categoria")
        dificultad = self.request.GET.get("dificultad")
        dificultades_validas = {
            Receta.Dificultad.FACIL,
            Receta.Dificultad.MEDIA,
            Receta.Dificultad.DIFICIL,
        }
        if dificultad in dificultades_validas:
            queryset = queryset.filter(dificultad=dificultad)
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query)
                | Q(ingredientes_receta__ingrediente__nombre__icontains=query)
            )
        if categoria and categoria.isdigit():
            queryset = queryset.filter(categorias__pk=categoria)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtros = self.request.GET.copy()
        filtros.pop("page", None)
        context["busqueda"] = self.request.GET.get("q", "")
        context["categoria_seleccionada"] = self.request.GET.get("categoria", "")
        context["dificultad_seleccionada"] = self.request.GET.get("dificultad")
        context["dificultades"] = Receta.Dificultad.choices
        context["categorias"] = Categoria.objects.all()
        context["filtros_query"] = filtros.urlencode()
        return context


class RecetaDetailView(DetailView):
    model = Receta
    template_name = "detalle_receta.html"
    context_object_name = "receta"

    def get_queryset(self):
        return get_receta_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pasos"] = [
            re.sub(r"^\d+\.\s*", "", paso.strip())
            for paso in re.split(r"\s+(?=\d+\.\s)", self.object.preparacion)
            if paso.strip()
        ]
        return context
