from django.views.generic import DetailView, ListView

from api.models import Receta


class RecetaListView(ListView):
    model = Receta
    template_name = "lista_recetas.html"
    context_object_name = "recetas"

    def get_queryset(self):
        return (
            Receta.objects.filter(estado=Receta.Estado.PUBLICADA)
            .select_related("cocinero")
            .prefetch_related("categorias", "ingredientes_receta__ingrediente")
        )


class RecetaDetailView(DetailView):
    model = Receta
    template_name = "detalle_receta.html"
    context_object_name = "receta"

    def get_queryset(self):
        return (
            Receta.objects.filter(estado=Receta.Estado.PUBLICADA)
            .select_related("cocinero")
            .prefetch_related("categorias", "ingredientes_receta__ingrediente")
        )
