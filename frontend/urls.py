from django.urls import path

from .views import RecetaDetailView, RecetaListView


app_name = "frontend"

urlpatterns = [
    path("", RecetaListView.as_view(), name="lista-recetas"),
    path("recetas/", RecetaListView.as_view(), name="lista-recetas-alias"),
    path("recetas/<int:pk>/", RecetaDetailView.as_view(), name="detalle-receta"),
]
