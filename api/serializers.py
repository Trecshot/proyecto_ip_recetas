from django.db import transaction
from rest_framework import serializers

from .models import (
    Auditoria,
    Categoria,
    Favorito,
    Ingrediente,
    Receta,
    RecetaIngrediente,
    Valoracion,
)


class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = ["id", "nombre", "unidad_medida", "stock"]

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion"]


class RecetaIngredienteSerializer(serializers.ModelSerializer):
    ingrediente = IngredienteSerializer(read_only=True)
    ingrediente_id = serializers.PrimaryKeyRelatedField(
        source="ingrediente", queryset=Ingrediente.objects.all(), write_only=True
    )

    class Meta:
        model = RecetaIngrediente
        fields = ["ingrediente", "ingrediente_id", "cantidad"]

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value


class RecetaSerializer(serializers.ModelSerializer):
    ingredientes = RecetaIngredienteSerializer(source="ingredientes_receta", many=True, read_only=True)
    ingredientes_data = RecetaIngredienteSerializer(many=True, write_only=True, required=False)
    cocinero_nombre = serializers.CharField(source="cocinero.username", read_only=True)
    promedio_puntuacion = serializers.FloatField(read_only=True)
    total_valoraciones = serializers.IntegerField(read_only=True)

    class Meta:
        model = Receta
        fields = [
            "id", "nombre", "descripcion", "preparacion", "tiempo_preparacion",
            "dificultad", "cocinero", "cocinero_nombre", "estado", "categorias",
            "ingredientes", "ingredientes_data", "promedio_puntuacion",
            "total_valoraciones", "created_at", "updated_at",
        ]
        read_only_fields = ["cocinero", "created_at", "updated_at"]

    def validate_tiempo_preparacion(self, value):
        if value <= 0:
            raise serializers.ValidationError("El tiempo debe ser mayor que cero.")
        return value

    def validate_ingredientes_data(self, value):
        ids = [item["ingrediente"].pk for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("No se puede repetir un ingrediente en la receta.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredientes_data", [])
        categories = validated_data.pop("categorias", [])
        recipe = Receta.objects.create(**validated_data)
        recipe.categorias.set(categories)
        self._save_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredientes_data", None)
        categories = validated_data.pop("categorias", None)
        recipe = super().update(instance, validated_data)
        if categories is not None:
            recipe.categorias.set(categories)
        if ingredients is not None:
            recipe.ingredientes_receta.all().delete()
            self._save_ingredients(recipe, ingredients)
        return recipe

    @staticmethod
    def _save_ingredients(recipe, ingredients):
        RecetaIngrediente.objects.bulk_create(
            [RecetaIngrediente(receta=recipe, **item) for item in ingredients]
        )


class ValoracionSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Valoracion
        fields = ["id", "usuario", "receta", "puntuacion", "comentario", "created_at"]
        read_only_fields = ["usuario", "created_at"]

    def validate(self, attrs):
        if attrs["receta"].estado != Receta.Estado.PUBLICADA:
            raise serializers.ValidationError("Solo se pueden valorar recetas publicadas.")
        return attrs


class FavoritoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Favorito
        fields = ["id", "usuario", "receta", "created_at"]
        read_only_fields = ["usuario", "created_at"]

    def validate_receta(self, value):
        if value.estado != Receta.Estado.PUBLICADA:
            raise serializers.ValidationError("Solo se pueden guardar recetas publicadas.")
        return value
