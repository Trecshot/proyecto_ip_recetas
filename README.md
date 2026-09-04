# API REST y Portal Web de Recetas

Aplicación culinaria construida con Django 5, Django REST Framework, `django-filter` y SQLite. Incluye una API REST y un portal web de recetas publicado en las rutas principales.

## 1. Requisitos

- Python 3.11 o superior.
- Git.
- PowerShell en Windows.

## 2. Instalación y puesta en marcha

Abre PowerShell dentro de la carpeta del proyecto antes de ejecutar los siguientes comandos.

En Windows PowerShell:

```powershell
# Crear el entorno virtual
python -m venv env

# Activar el entorno virtual
.\env\Scripts\Activate.ps1

# Si PowerShell bloquea la activación, habilitar scripts para el usuario actual
# y volver a ejecutar la línea anterior:
# Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# Actualizar pip e instalar Django y el resto de dependencias
python -m pip install --upgrade pip
# Este archivo instala Django y las dependencias de la API.
python -m pip install -r requirements.txt
```

`requirements.txt` instala Django, Django REST Framework, `django-filter`, drf-spectacular, drf-spectacular-sidecar y Faker. No es necesario ejecutar `startproject` ni `startapp`, porque el proyecto ya contiene `config/` y sus aplicaciones.

Aplica las migraciones, carga los datos gastronómicos de prueba y arranca el servidor:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py check
python manage.py test
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en el navegador. Para detener el servidor, pulsa `Ctrl+C`. Para salir del entorno virtual después de trabajar, ejecuta `deactivate`.


El comando `seed_data` limpia y reconstruye las recetas, categorías e ingredientes de demostración, y crea los grupos `Administrador`, `Cocinero` y `Usuario`, además de usuarios de prueba. Las contraseñas de ejemplo solo son para desarrollo y deben cambiarse.

### Consideraciones importantes

- `db.sqlite3` no se versiona. Al clonar el proyecto en otro equipo, ejecuta `migrate` y `seed_data` para crear la base de datos y cargar los datos de demostración.
- `seed_data` elimina y reconstruye los datos de recetas, categorías e ingredientes. Úsalo únicamente en desarrollo y no sobre una base de datos con información real.
- `makemigrations` solo es necesario después de modificar los modelos. En una instalación limpia ya existe la migración inicial, por lo que normalmente basta con ejecutar `migrate`.
- La configuración actual es para desarrollo local: usa `DEBUG = True`, una clave secreta de ejemplo y hosts locales. Debe ajustarse antes de publicar la aplicación.
- El portal web carga Bootstrap desde jsDelivr, por lo que necesita conexión a Internet para mostrar correctamente sus estilos.

## 3. URLs de la aplicación

### Portal web

- `/`: listado visual de recetas publicadas.
- `/recetas/`: listado visual de recetas publicadas.
- `/recetas/{id}/`: detalle de una receta.

### API REST

Solicita un token con `POST /api/auth/token/` enviando `username` y `password`, y usa `Authorization: Token <token>` en las peticiones protegidas.

Recursos principales:

- `/api/recetas/`
- `/api/ingredientes/`
- `/api/categorias/`
- `/api/valoraciones/`
- `/api/favoritos/`

Acciones de receta (métodos POST sobre la ruta de detalle):

- `/api/recetas/{id}/enviar-revision/`
- `/api/recetas/{id}/publicar/`
- `/api/recetas/{id}/archivar/`

Filtros disponibles en recetas: `nombre`, `categoria`, `cocinero`, `dificultad`, `estado`, `tiempo_maximo` e `ingrediente`.
Ordenamiento: `?ordering=nombre`, `?ordering=-created_at`, `?ordering=-total_valoraciones`, `?ordering=-promedio_puntuacion`.

Reportes:

- `/api/reportes/recetas/`
- `/api/reportes/usuarios/`
- `/api/reportes/ingredientes/`
- `/api/reportes/valoraciones/`

Documentación interactiva:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- Esquema OpenAPI (JSON): `/api/schema/`

## 4. Ejemplos JSON y comandos útiles

Obtener token (curl):

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ -d "username=cocinero&password=Cocinero12345!"
```

Ejemplo: crear una receta (como `Cocinero`) — POST `/api/recetas/` (JSON):

```json
{
    "nombre": "Sopa de verduras",
    "descripcion": "Sopa casera de temporada.",
    "preparacion": "Cortar, sofreír, cubrir con agua y cocer.",
    "tiempo_preparacion": 45,
    "dificultad": "FACIL",
    "categorias": [1],
    "ingredientes_data": [
        {"ingrediente_id": 1, "cantidad": "300.000"},
        {"ingrediente_id": 2, "cantidad": "10.000"}
    ]
}
```

Ejemplo: cambiar estado respetando la máquina de estados (PATCH parcial) — PATCH `/api/recetas/{id}/`:

```json
{ "estado": "REVISION" }
```

O usar el endpoint de acción (POST):

```bash
curl -X POST -H "Authorization: Token <token>" http://127.0.0.1:8000/api/recetas/1/enviar-revision/
```

## 5. Estructura del proyecto

- `api/`: modelos, serializers, ViewSets, filtros y endpoints REST.
- `frontend/`: vistas basadas en clases y URLs del portal web.
- `templates/`: plantillas HTML con herencia Django y Bootstrap 5.
- `config/`: configuración global y enrutamiento principal.
- `db.sqlite3`: base de datos SQLite local.
- `manage.py`: comandos administrativos de Django.

La API permanece desacoplada bajo `/api/`, mientras que las vistas HTML se sirven desde `/` y `/recetas/`.

## 6. Desarrollo y mantenimiento

Para comprobar la configuración del proyecto:

```powershell
python manage.py check
```

Las transiciones inválidas de estado responden HTTP 400 y no modifican la receta. Cada transición válida actualiza la receta y registra `HistorialReceta` y `Auditoria` dentro de una transacción atómica.