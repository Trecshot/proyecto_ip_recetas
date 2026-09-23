from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ip_recetas.models import Receta


class RecetaAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cocinero", password="Cocinero12345!")
        self.public_recipe = Receta.objects.create(
            nombre="Tortilla de patata",
            descripcion="Una receta sencilla.",
            preparacion="Cocinar y servir.",
            tiempo_preparacion=20,
            tiempo_coccion=15,
            dificultad=Receta.Dificultad.FACIL,
            cocinero=self.user,
            estado=Receta.Estado.PUBLICADA,
        )

    def test_obtener_lista_recetas_publicadas(self):
        response = self.client.get(reverse("receta-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nombre"], self.public_recipe.nombre)

    def test_crear_receta_requiere_autenticacion(self):
        payload = {
            "nombre": "Sopa de verduras",
            "descripcion": "Sopa casera.",
            "preparacion": "Cocer las verduras.",
            "tiempo_preparacion": 30,
            "tiempo_coccion": 20,
            "dificultad": Receta.Dificultad.FACIL,
        }

        response = self.client.post(reverse("receta-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("receta-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cocinero"], self.user.pk)
        self.assertEqual(Receta.objects.filter(nombre="Sopa de verduras").count(), 1)

    def test_reportes_requieren_autenticacion(self):
        url = reverse("reporte-recetas")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["total"], 1)
