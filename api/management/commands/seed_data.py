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
    {
        "nombre": "Risotto de Champiñones y Parmesano",
        "categoria": "Platos de Fondo / Cocina Italiana",
        "dificultad": "MEDIA",
        "tiempo": 45,
        "descripcion": "Arroz arborio cremoso cocinado lentamente con caldo de verduras, champiñones frescos, vino blanco, mantequilla y queso parmesano.",
        "preparacion": "1. Dorar los champiñones a fuego alto con aceite y reservar. 2. Sofreír la cebolla y el ajo hasta transparentar. 3. Incorporar el arroz y tostarlo durante 2 minutos. 4. Añadir el vino blanco y remover hasta que se evapore. 5. Agregar el caldo caliente de a cucharones, removiendo y esperando que se absorba antes de añadir más, durante 16 a 18 minutos. 6. Retirar del fuego y añadir los champiñones, la mantequilla fría y el parmesano. 7. Remover enérgicamente durante 1 minuto, tapar 2 minutos y servir.",
        "ingredientes": [
            {"cantidad": 320, "unidad": "gramos", "nombre": "Arroz arborio o carnaroli"},
            {"cantidad": 300, "unidad": "gramos", "nombre": "Champiñones fileteados"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Cebolla blanca pequeña"},
            {"cantidad": 2, "unidad": "unidades", "nombre": "Dientes de ajo"},
            {"cantidad": 100, "unidad": "mililitros", "nombre": "Vino blanco seco"},
            {"cantidad": 1000, "unidad": "mililitros", "nombre": "Caldo de verduras"},
            {"cantidad": 50, "unidad": "gramos", "nombre": "Mantequilla sin sal"},
            {"cantidad": 60, "unidad": "gramos", "nombre": "Queso parmesano rallado"},
            {"cantidad": 2, "unidad": "cucharadas", "nombre": "Aceite de oliva"},
        ],
    },
    {
        "nombre": "Salmón al Horno con Costra de Finas Hierbas y Limón",
        "categoria": "Pescados y Mariscos / Saludable",
        "dificultad": "FACIL",
        "tiempo": 25,
        "descripcion": "Filetes de salmón jugosos cubiertos con una costra crocante de pan rallado, hierbas frescas, limón y aceite de oliva.",
        "preparacion": "1. Precalentar el horno a 200 °C y preparar una bandeja. 2. Secar los filetes, colocarlos con la piel hacia abajo y sazonarlos. 3. Mezclar el pan rallado con perejil, eneldo, ajo, ralladura de limón, sal y aceite. 4. Distribuir la mezcla sobre el salmón y presionar suavemente. 5. Hornear durante 12 a 15 minutos hasta que la costra esté dorada y el centro tierno. 6. Servir con ensalada verde o verduras asadas.",
        "ingredientes": [
            {"cantidad": 2, "unidad": "unidades", "nombre": "Filetes de salmón fresco"},
            {"cantidad": 3, "unidad": "cucharadas", "nombre": "Pan rallado o panko"},
            {"cantidad": 1, "unidad": "cucharada", "nombre": "Perejil fresco picado"},
            {"cantidad": 1, "unidad": "cucharadita", "nombre": "Eneldo o tomillo fresco"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Limón amarillo"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Diente de ajo rallado"},
            {"cantidad": 2, "unidad": "cucharadas", "nombre": "Aceite de oliva virgen extra"},
        ],
    },
    {
        "nombre": "Shakshuka Tradicional",
        "categoria": "Desayuno / Almuerzo rápido",
        "dificultad": "FACIL",
        "tiempo": 30,
        "descripcion": "Huevos escalfados en una salsa espesa de tomates, pimientos, cebolla, comino y pimentón dulce.",
        "preparacion": "1. Calentar el aceite en una sartén amplia. 2. Cocinar la cebolla y el pimiento durante 7 a 8 minutos. 3. Añadir el ajo, comino, pimentón y chile, y sofreír 1 minuto. 4. Incorporar los tomates, salpimentar y reducir durante 10 minutos. 5. Hacer cuatro huecos y romper un huevo en cada uno. 6. Tapar y cocinar 5 a 8 minutos, hasta cuajar las claras. 7. Terminar con queso feta y cilantro o perejil.",
        "ingredientes": [
            {"cantidad": 4, "unidad": "unidades", "nombre": "Huevos de campo"},
            {"cantidad": 400, "unidad": "gramos", "nombre": "Tomate triturado"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Pimiento rojo"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Cebolla mediana"},
            {"cantidad": 2, "unidad": "unidades", "nombre": "Dientes de ajo laminados"},
            {"cantidad": 1, "unidad": "cucharadita", "nombre": "Comino molido"},
            {"cantidad": 1, "unidad": "cucharadita", "nombre": "Pimentón dulce"},
            {"cantidad": 50, "unidad": "gramos", "nombre": "Queso feta"},
            {"cantidad": 2, "unidad": "cucharadas", "nombre": "Aceite de oliva"},
        ],
    },
    {
        "nombre": "Curry Suave de Pollo con Leche de Coco",
        "categoria": "Platos de Fondo / Cocina Asiática",
        "dificultad": "MEDIA",
        "tiempo": 40,
        "descripcion": "Pollo sellado cocinado en una salsa aromática de leche de coco, curry amarillo, jengibre y verduras.",
        "preparacion": "1. Sazonar el pollo con sal y una cucharadita de curry. 2. Dorarlo en aceite a fuego alto y reservar. 3. Sofreír cebolla, zanahoria, ajo y jengibre. 4. Añadir el resto del curry durante 30 segundos. 5. Verter la leche de coco y la salsa de soya. 6. Reincorporar el pollo y cocinar a fuego bajo durante 15 minutos. 7. Añadir el jugo de limón y cilantro antes de servir con arroz basmati.",
        "ingredientes": [
            {"cantidad": 600, "unidad": "gramos", "nombre": "Pechuga de pollo en cubos"},
            {"cantidad": 400, "unidad": "mililitros", "nombre": "Leche de coco"},
            {"cantidad": 2, "unidad": "cucharadas", "nombre": "Curry en polvo"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Cebolla morada"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Zanahoria"},
            {"cantidad": 2, "unidad": "centímetros", "nombre": "Jengibre fresco"},
            {"cantidad": 2, "unidad": "unidades", "nombre": "Dientes de ajo picados"},
            {"cantidad": 1, "unidad": "cucharada", "nombre": "Salsa de soya"},
            {"cantidad": 0.5, "unidad": "unidad", "nombre": "Limón"},
        ],
    },
    {
        "nombre": "Lentejas Guisadas con Verduras y Pimentón",
        "categoria": "Sopas y Guisos / Legumbres",
        "dificultad": "FACIL",
        "tiempo": 55,
        "descripcion": "Guiso reconfortante y nutritivo de lentejas con cebolla, zanahoria, zapallo, papa y pimentón ahumado.",
        "preparacion": "1. Sofreír la cebolla, el pimiento y el ajo durante 5 minutos. 2. Añadir el pimentón y el comino. 3. Incorporar zanahoria, papa, zapallo y lentejas. 4. Cubrir con caldo, añadir laurel y sal. 5. Hervir, bajar el fuego y cocinar parcialmente tapado durante 30 a 35 minutos. 6. Rectificar la sazón, retirar el laurel y reposar 5 minutos.",
        "ingredientes": [
            {"cantidad": 300, "unidad": "gramos", "nombre": "Lentejas"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Zanahoria grande"},
            {"cantidad": 150, "unidad": "gramos", "nombre": "Zapallo camote"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Papa mediana"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Cebolla mediana"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Pimiento verde o rojo"},
            {"cantidad": 2, "unidad": "unidades", "nombre": "Dientes de ajo"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Hoja de laurel"},
            {"cantidad": 1, "unidad": "litro", "nombre": "Caldo de verduras"},
        ],
    },
    {
        "nombre": "Pasta al Pesto Genovés Clásico",
        "categoria": "Pastas / Rápida",
        "dificultad": "FACIL",
        "tiempo": 25,
        "descripcion": "Pasta servida con una emulsión fresca de albahaca, piñones, parmesano, pecorino y aceite de oliva virgen extra.",
        "preparacion": "1. Tostar los piñones durante 2 minutos y dejar enfriar. 2. Procesar el ajo con sal y los piñones. 3. Añadir la albahaca en pulsos cortos. 4. Incorporar los quesos y el aceite en hilo hasta emulsionar. 5. Cocer la pasta al dente y reservar media taza de agua. 6. Mezclar la pasta con el pesto fuera del fuego, ajustando la textura con el agua reservada.",
        "ingredientes": [
            {"cantidad": 400, "unidad": "gramos", "nombre": "Pasta"},
            {"cantidad": 60, "unidad": "gramos", "nombre": "Hojas de albahaca fresca"},
            {"cantidad": 30, "unidad": "gramos", "nombre": "Piñones o nueces"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Diente de ajo"},
            {"cantidad": 50, "unidad": "gramos", "nombre": "Queso parmesano rallado"},
            {"cantidad": 20, "unidad": "gramos", "nombre": "Queso pecorino rallado"},
            {"cantidad": 100, "unidad": "mililitros", "nombre": "Aceite de oliva virgen extra"},
            {"cantidad": 1, "unidad": "pizca", "nombre": "Sal fina"},
        ],
    },
    {
        "nombre": "Ensalada Mediterránea de Garbanzos y Pepino",
        "categoria": "Ensaladas / Fresca",
        "dificultad": "FACIL",
        "tiempo": 15,
        "descripcion": "Ensalada fresca y saciante de garbanzos, pepino, tomates cherry, aceitunas negras, feta, limón y orégano.",
        "preparacion": "1. Remojar la cebolla en agua fría durante 5 minutos si su sabor es intenso. 2. Combinar garbanzos, pepino, tomates, aceitunas y cebolla. 3. Emulsionar aceite, limón, orégano, sal y pimienta. 4. Verter el aderezo y mezclar suavemente. 5. Terminar con feta y perejil justo antes de servir.",
        "ingredientes": [
            {"cantidad": 400, "unidad": "gramos", "nombre": "Garbanzos cocidos"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Pepino mediano"},
            {"cantidad": 150, "unidad": "gramos", "nombre": "Tomates cherry"},
            {"cantidad": 0.5, "unidad": "unidad", "nombre": "Cebolla morada"},
            {"cantidad": 60, "unidad": "gramos", "nombre": "Aceitunas negras"},
            {"cantidad": 80, "unidad": "gramos", "nombre": "Queso feta en cubos"},
            {"cantidad": 2, "unidad": "cucharadas", "nombre": "Perejil fresco picado"},
            {"cantidad": 3, "unidad": "cucharadas", "nombre": "Aceite de oliva virgen extra"},
            {"cantidad": 1.5, "unidad": "cucharadas", "nombre": "Jugo de limón"},
        ],
    },
    {
        "nombre": "Crema Ligera de Zapallo y Jengibre",
        "categoria": "Sopas y Cremas / Entradas",
        "dificultad": "FACIL",
        "tiempo": 40,
        "descripcion": "Sopa aterciopelada de zapallo y papa con puerro, jengibre y semillas tostadas para aportar textura.",
        "preparacion": "1. Rehogar el puerro en aceite durante 4 minutos. 2. Añadir el jengibre y mezclar 30 segundos. 3. Incorporar zapallo y papa, y cubrir con caldo. 4. Hervir, bajar el fuego y cocinar tapado durante 20 minutos. 5. Procesar hasta obtener una textura lisa. 6. Añadir crema opcional, sal, pimienta y nuez moscada. 7. Servir con aceite de oliva y semillas tostadas.",
        "ingredientes": [
            {"cantidad": 700, "unidad": "gramos", "nombre": "Zapallo camote"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Puerro"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Papa mediana"},
            {"cantidad": 1, "unidad": "cucharadita", "nombre": "Jengibre fresco rallado"},
            {"cantidad": 600, "unidad": "mililitros", "nombre": "Caldo de verduras"},
            {"cantidad": 100, "unidad": "mililitros", "nombre": "Crema de leche"},
            {"cantidad": 2, "unidad": "cucharadas", "nombre": "Semillas de zapallo"},
            {"cantidad": 2, "unidad": "cucharadas", "nombre": "Aceite de oliva"},
        ],
    },
    {
        "nombre": "Fajitas de Carne Salteadas con Pimientos",
        "categoria": "Platos de Fondo / Tex-Mex",
        "dificultad": "FACIL",
        "tiempo": 30,
        "descripcion": "Tiras tiernas de carne de res selladas a fuego vivo con pimientos tricolor, cebolla y sazón tradicional.",
        "preparacion": "1. Marinar la carne con ajo, comino, ají de color, salsa inglesa, limón, sal, pimienta y aceite durante 15 minutos. 2. Calentar una sartén a fuego muy alto y sellar la carne en una sola capa durante 2 a 3 minutos por lado. 3. Retirar y saltear cebolla y pimientos durante 3 a 4 minutos. 4. Devolver la carne y sus jugos, mezclar 1 minuto y servir con tortillas calientes.",
        "ingredientes": [
            {"cantidad": 500, "unidad": "gramos", "nombre": "Carne de res en tiras"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Pimiento rojo"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Pimiento verde"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Cebolla blanca grande"},
            {"cantidad": 2, "unidad": "unidades", "nombre": "Dientes de ajo"},
            {"cantidad": 1, "unidad": "cucharadita", "nombre": "Comino en polvo"},
            {"cantidad": 1, "unidad": "cucharadita", "nombre": "Ají de color"},
            {"cantidad": 1, "unidad": "cucharada", "nombre": "Salsa inglesa"},
            {"cantidad": 1, "unidad": "unidad", "nombre": "Lima o limón"},
            {"cantidad": 8, "unidad": "unidades", "nombre": "Tortillas de trigo"},
        ],
    },
    {
        "nombre": "Brownie Húmedo de Chocolate Amargo y Nueces",
        "categoria": "Postres y Repostería",
        "dificultad": "FACIL",
        "tiempo": 40,
        "descripcion": "Brownie con corteza craquelada y centro húmedo y denso, elaborado con chocolate semiamargo y nueces crocantes.",
        "preparacion": "1. Precalentar el horno a 175 °C y preparar un molde cuadrado de 20 x 20 cm. 2. Derretir chocolate y mantequilla, y dejar entibiar. 3. Batir huevos, azúcar y vainilla durante 2 a 3 minutos. 4. Integrar el chocolate fundido. 5. Tamizar harina, cacao y sal, e incorporar sin batir de más. 6. Añadir las nueces y verter en el molde. 7. Hornear 22 a 25 minutos, hasta que el palillo salga con migas húmedas. 8. Enfriar antes de cortar.",
        "ingredientes": [
            {"cantidad": 200, "unidad": "gramos", "nombre": "Chocolate semiamargo"},
            {"cantidad": 120, "unidad": "gramos", "nombre": "Mantequilla sin sal"},
            {"cantidad": 150, "unidad": "gramos", "nombre": "Azúcar blanca"},
            {"cantidad": 3, "unidad": "unidades", "nombre": "Huevos"},
            {"cantidad": 70, "unidad": "gramos", "nombre": "Harina de trigo"},
            {"cantidad": 25, "unidad": "gramos", "nombre": "Cacao amargo en polvo"},
            {"cantidad": 1, "unidad": "cucharadita", "nombre": "Extracto de vainilla"},
            {"cantidad": 80, "unidad": "gramos", "nombre": "Nueces picadas"},
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
                f"y {len(RECETAS_DATA)} recetas reales creadas."
            )
        )
