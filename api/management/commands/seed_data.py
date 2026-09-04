from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Categoria, Ingrediente, Receta, RecetaIngrediente


RECETAS_DATA = [
    {
        "nombre": "Espaguetis a la Carbonara Clásica",
        "categoria": "Platos Principales",
        "dificultad": "MEDIA",
        "tiempo": 25,
        "descripcion": "Plato tradicional romano elaborado con guanciale, queso pecorino, huevo y pimienta negra. Requiere control térmico para evitar la coagulación del huevo.",
        "preparacion": "1. Hervir la pasta en agua con sal hasta alcanzar textura al dente. 2. Sofreír el guanciale sin aceites añadidos hasta que libere su grasa y esté crujiente. 3. En un bol aparte, emulsionar las yemas con el queso pecorino. 4. Integrar la pasta caliente con el guanciale y añadir la emulsión de huevo fuera del fuego, mezclando vigorosamente. 5. Servir inmediatamente con pimienta negra recién molida.",
        "ingredientes": [
            {"cantidad": 400, "unidad": "gramos", "nombre": "Espaguetis"},
            {"cantidad": 150, "unidad": "gramos", "nombre": "Guanciale"},
            {"cantidad": 4, "unidad": "unidades", "nombre": "Yemas de huevo"},
            {"cantidad": 100, "unidad": "gramos", "nombre": "Queso Pecorino Romano"},
            {"cantidad": 5, "unidad": "gramos", "nombre": "Pimienta negra"},
        ],
    },
    {
        "nombre": "Ceviche Clásico de Reineta",
        "categoria": "Entrantes",
        "dificultad": "FACIL",
        "tiempo": 30,
        "descripcion": "Preparación fría de pescado blanco sometido a desnaturalización proteica mediante el ácido cítrico del limón, acompañado de vegetales crujientes.",
        "preparacion": "1. Limpiar el filete de reineta y cortarlo en cubos uniformes de 1.5 cm. 2. Picar la cebolla morada en pluma fina y amortiguarla en agua fría. 3. Picar el cilantro finamente. 4. Exprimir los limones asegurando no presionar la cáscara para evitar aceites amargos. 5. Mezclar el pescado, la cebolla, el cilantro y la sal, verter el jugo de limón y dejar reposar refrigerado por 15 minutos exactos.",
        "ingredientes": [
            {"cantidad": 500, "unidad": "gramos", "nombre": "Filete de Reineta"},
            {"cantidad": 10, "unidad": "unidades", "nombre": "Limones de Pica"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Cebolla morada"},
            {"cantidad": 50, "unidad": "gramos", "nombre": "Cilantro fresco"},
            {"cantidad": 10, "unidad": "gramos", "nombre": "Sal de mar"},
        ],
    },
    {
        "nombre": "Tiramisú Italiano Tradicional",
        "categoria": "Postres",
        "dificultad": "MEDIA",
        "tiempo": 45,
        "descripcion": "Postre frío de estratificación, compuesto por capas de bizcochos humedecidos en café expreso y una crema untuosa a base de queso mascarpone y huevos.",
        "preparacion": "1. Preparar el café espresso y dejar enfriar a temperatura ambiente. 2. Separar las yemas de las claras. 3. Batir las yemas con el azúcar hasta que blanqueen, luego incorporar el queso mascarpone a baja velocidad. 4. Montar las claras a punto de nieve e incorporar a la mezcla anterior con movimientos envolventes. 5. Sumergir ligeramente los bizcochos en el café y disponerlos en una fuente, alternando capas de bizcocho y crema. 6. Refrigerar por 4 horas y espolvorear cacao puro antes de servir.",
        "ingredientes": [
            {"cantidad": 300, "unidad": "gramos", "nombre": "Queso Mascarpone"},
            {"cantidad": 200, "unidad": "mililitros", "nombre": "Café espresso frío"},
            {"cantidad": 3, "unidad": "unidades", "nombre": "Huevos"},
            {"cantidad": 100, "unidad": "gramos", "nombre": "Azúcar granulada"},
            {"cantidad": 200, "unidad": "gramos", "nombre": "Bizcochos (Savoiardi)"},
        ],
    },
    {
        "nombre": "Ensalada César con Pollo Asado",
        "categoria": "Ensaladas",
        "dificultad": "FACIL",
        "tiempo": 20,
        "descripcion": "Ensalada internacional caracterizada por el contraste de texturas entre la lechuga crujiente, los crutones deshidratados y la emulsión salina del aderezo.",
        "preparacion": "1. Salpimentar la pechuga de pollo y asar a la plancha hasta alcanzar 74°C en el centro; dejar reposar y cortar en tiras. 2. Lavar, secar rigurosamente y trocear la lechuga romana con las manos para evitar oxidación. 3. En un bol amplio, disponer la lechuga y masajear levemente con el aderezo. 4. Incorporar los crutones, las lascas de queso parmesano y las tiras de pollo. 5. Servir de inmediato para mantener la rigidez de los vegetales.",
        "ingredientes": [
            {"cantidad": 1, "unidad": "unidad", "nombre": "Lechuga Romana grande"},
            {"cantidad": 200, "unidad": "gramos", "nombre": "Pechuga de pollo"},
            {"cantidad": 50, "unidad": "gramos", "nombre": "Queso Parmesano en trozo"},
            {"cantidad": 100, "unidad": "gramos", "nombre": "Crutones de pan de masa madre"},
            {"cantidad": 45, "unidad": "mililitros", "nombre": "Aderezo César comercial o casero"},
        ],
    },
    {
        "nombre": "Pastel de Choclo Tradicional",
        "categoria": "Platos Principales",
        "dificultad": "DIFICIL",
        "tiempo": 90,
        "descripcion": "Pastel salado-dulce horneado. Consta de una base de proteína animal guisada (pino) sellada bajo una espesa pasta de maíz caramelizada.",
        "preparacion": "1. Sofreír la cebolla picada con la carne molida, condimentar con comino y sal, cocinar hasta que la cebolla esté traslúcida (pino). 2. Rallar los choclos y cocinar la pasta obtenida a fuego medio junto con la albahaca picada y leche si está muy espesa, revolviendo constantemente por 15 minutos. 3. En platos de greda, disponer una base de pino, agregar un trutro de pollo cocido, huevo duro opcional y cubrir homogéneamente con la pasta de choclo. 4. Espolvorear azúcar granulada en la superficie y hornear a 200°C hasta obtener una costra dorada y caramelizada.",
        "ingredientes": [
            {"cantidad": 6, "unidad": "unidades", "nombre": "Choclos pasteleros crudos"},
            {"cantidad": 500, "unidad": "gramos", "nombre": "Carne molida de vacuno (4% grasa)"},
            {"cantidad": 2, "unidad": "unidades", "nombre": "Cebollas grandes"},
            {"cantidad": 4, "unidad": "unidades", "nombre": "Trutros de pollo cocidos"},
            {"cantidad": 15, "unidad": "gramos", "nombre": "Hojas de Albahaca fresca"},
        ],
    },
]


class Command(BaseCommand):
    help = "Puebla la base de datos con roles, usuarios, categorías, ingredientes y recetas de prueba."

    def _create_roles_and_users(self):
        roles = {}
        for name in ("Administrador", "Cocinero", "Usuario"):
            roles[name], _ = Group.objects.get_or_create(name=name)

        admin, _ = User.objects.get_or_create(username="admin")
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Admin12345!")
        admin.save()
        roles["Administrador"].user_set.add(admin)

        cook, _ = User.objects.get_or_create(username="cocinero")
        cook.set_password("Cocinero12345!")
        cook.save()
        roles["Cocinero"].user_set.add(cook)

        user, _ = User.objects.get_or_create(username="usuario")
        user.set_password("Usuario12345!")
        user.save()
        roles["Usuario"].user_set.add(user)

        return admin, cook, user

    def _create_master_data(self):
        category_names = sorted({recipe["categoria"] for recipe in RECETAS_DATA})
        categories = {}
        for name in category_names:
            categories[name], _ = Categoria.objects.update_or_create(
                nombre=name,
                defaults={"descripcion": f"Recetas de {name.lower()}"},
            )

        ingredient_data = {
            ingredient["nombre"]: ingredient
            for recipe in RECETAS_DATA
            for ingredient in recipe["ingredientes"]
        }
        ingredients = {}
        for name, data in ingredient_data.items():
            ingredients[name], _ = Ingrediente.objects.update_or_create(
                nombre=name,
                defaults={
                    "unidad_medida": data["unidad"],
                    "stock": Decimal("1000"),
                },
            )

        return categories, ingredients

    @transaction.atomic
    def handle(self, *args, **options):
        admin, cook, user = self._create_roles_and_users()

        # Se eliminan primero las recetas para liberar sus relaciones protegidas.
        Receta.objects.all().delete()
        Ingrediente.objects.all().delete()
        Categoria.objects.all().delete()

        categories, ingredients = self._create_master_data()

        for recipe_data in RECETAS_DATA:
            receta = Receta.objects.create(
                nombre=recipe_data["nombre"],
                descripcion=recipe_data["descripcion"],
                preparacion=recipe_data["preparacion"],
                tiempo_preparacion=recipe_data["tiempo"],
                dificultad=recipe_data["dificultad"],
                cocinero=cook,
                estado=Receta.Estado.PUBLICADA,
            )
            receta.categorias.add(categories[recipe_data["categoria"]])

            for ingredient_data in recipe_data["ingredientes"]:
                RecetaIngrediente.objects.create(
                    receta=receta,
                    ingrediente=ingredients[ingredient_data["nombre"]],
                    cantidad=Decimal(str(ingredient_data["cantidad"])),
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed completado: roles, usuarios, categorías, ingredientes "
                "y 5 recetas reales creadas."
            )
        )
