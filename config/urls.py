from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from api.views import api_home

# drf-spectacular views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Portal web y punto de entrada de la API.
    path("", include("frontend.urls")),
    path("api/info/", api_home, name="api-home"),
    path("admin/", admin.site.urls),
    # Login/logout para la Browsable API de DRF.
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/auth/token/", obtain_auth_token, name="api-token"),
    # Esquema OpenAPI y sus interfaces Swagger y ReDoc.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/", include("api.urls")),
]
