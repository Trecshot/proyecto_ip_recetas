import django_filters
from django.db.models import Avg, Count

from .models import Receta


class RecetaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(field_name="nombre", lookup_expr="icontains")
    categoria = django_filters.CharFilter(field_name="categorias__nombre", lookup_expr="iexact")
    cocinero = django_filters.NumberFilter(field_name="cocinero_id")
    dificultad = django_filters.CharFilter(field_name="dificultad", lookup_expr="iexact")
    estado = django_filters.CharFilter(field_name="estado", lookup_expr="iexact")
    tiempo_maximo = django_filters.NumberFilter(field_name="tiempo_preparacion", lookup_expr="lte")
    ingrediente = django_filters.CharFilter(field_name="ingredientes_receta__ingrediente__nombre", lookup_expr="icontains")

    class Meta:
        model = Receta
        fields = ["nombre", "categoria", "cocinero", "dificultad", "estado", "tiempo_maximo", "ingrediente"]
