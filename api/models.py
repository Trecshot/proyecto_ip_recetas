from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Receta(models.Model):
    class Dificultad(models.TextChoices):
        FACIL = "FACIL", "Fácil"
        MEDIA = "MEDIA", "Media"
        DIFICIL = "DIFICIL", "Difícil"

    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        REVISION = "REVISION", "En revisión"
        PUBLICADA = "PUBLICADA", "Publicada"
        ARCHIVADA = "ARCHIVADA", "Archivada"

    nombre = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True)
    preparacion = models.TextField()
    tiempo_preparacion = models.PositiveIntegerField(help_text="Minutos")
    dificultad = models.CharField(max_length=10, choices=Dificultad.choices)
    cocinero = models.ForeignKey(User, on_delete=models.PROTECT, related_name="recetas")
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.BORRADOR)
    categorias = models.ManyToManyField("Categoria", related_name="recetas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(tiempo_preparacion__gt=0),
                name="receta_tiempo_positivo",
            ),
        ]

    def __str__(self):
        return self.nombre


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    unidad_medida = models.CharField(max_length=40)
    stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(condition=models.Q(stock__gte=0), name="ingrediente_stock_no_negativo"),
        ]

    def __str__(self):
        return self.nombre


class RecetaIngrediente(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="ingredientes_receta")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT, related_name="recetas_ingrediente")
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["receta", "ingrediente"], name="receta_ingrediente_unico"),
            models.CheckConstraint(condition=models.Q(cantidad__gt=0), name="cantidad_ingrediente_positiva"),
        ]


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Valoracion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="valoraciones")
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="valoraciones")
    puntuacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "receta"], name="valoracion_usuario_receta_unica"),
            models.CheckConstraint(condition=models.Q(puntuacion__gte=1, puntuacion__lte=5), name="puntuacion_valida"),
        ]


class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favoritos")
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="favoritos")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "receta"], name="favorito_usuario_receta_unico"),
        ]


class HistorialReceta(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.PROTECT, related_name="historial")
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="historial_recetas")
    accion = models.CharField(max_length=40)
    estado_anterior = models.CharField(max_length=10, choices=Receta.Estado.choices, blank=True)
    estado_nuevo = models.CharField(max_length=10, choices=Receta.Estado.choices)
    fecha = models.DateTimeField(auto_now_add=True)
    detalle = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha"]


class Auditoria(models.Model):
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="auditorias")
    accion = models.CharField(max_length=80)
    modelo = models.CharField(max_length=100)
    objeto_id = models.PositiveBigIntegerField(null=True, blank=True)
    detalle = models.JSONField(default=dict, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
