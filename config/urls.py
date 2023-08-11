from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),  # type: ignore
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),  # type: ignore
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/events/", include("core.bookings.urls")),
    path("api/hotels/", include("core.hotels.urls")),
]

if settings.DEBUG:
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))  # type: ignore
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))  # type: ignore
