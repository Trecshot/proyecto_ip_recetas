from django.contrib import admin

from .models import Auditoria, Categoria, Favorito, HistorialReceta, Ingrediente, Receta, RecetaIngrediente, Valoracion


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cocinero", "dificultad", "estado", "tiempo_preparacion", "created_at")
    search_fields = ("nombre", "descripcion", "cocinero__username")
    list_filter = ("estado", "dificultad", "categorias")


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "unidad_medida", "stock")
    search_fields = ("nombre",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(RecetaIngrediente)
class RecetaIngredienteAdmin(admin.ModelAdmin):
    list_display = ("receta", "ingrediente", "cantidad")
    search_fields = ("receta__nombre", "ingrediente__nombre")


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ("receta", "usuario", "puntuacion", "created_at")
    search_fields = ("receta__nombre", "usuario__username", "comentario")
    list_filter = ("puntuacion",)


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "receta", "created_at")
    search_fields = ("usuario__username", "receta__nombre")


@admin.register(HistorialReceta)
class HistorialRecetaAdmin(admin.ModelAdmin):
    list_display = ("receta", "accion", "estado_anterior", "estado_nuevo", "fecha", "usuario")
    list_filter = ("accion", "estado_nuevo")
    search_fields = ("receta__nombre", "usuario__username")
    readonly_fields = [field.name for field in HistorialReceta._meta.fields]


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ("accion", "modelo", "objeto_id", "usuario", "fecha")
    list_filter = ("accion", "modelo")
    search_fields = ("modelo", "usuario__username")
    readonly_fields = [field.name for field in Auditoria._meta.fields]
