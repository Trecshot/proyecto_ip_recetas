from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet,
    FavoritoViewSet,
    IngredienteViewSet,
    RecetaViewSet,
    ValoracionViewSet,
    reporte_ingredientes,
    reporte_recetas,
    reporte_usuarios,
    reporte_valoraciones,
)

router = DefaultRouter()
router.register("recetas", RecetaViewSet, basename="receta")
router.register("ingredientes", IngredienteViewSet, basename="ingrediente")
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("valoraciones", ValoracionViewSet, basename="valoracion")
router.register("favoritos", FavoritoViewSet, basename="favorito")

urlpatterns = [
    path("reportes/recetas/", reporte_recetas, name="reporte-recetas"),
    path("reportes/usuarios/", reporte_usuarios, name="reporte-usuarios"),
    path("reportes/ingredientes/", reporte_ingredientes, name="reporte-ingredientes"),
    path("reportes/valoraciones/", reporte_valoraciones, name="reporte-valoraciones"),
]
urlpatterns += router.urls
