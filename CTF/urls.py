from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from challenge.views import check_answer
from main.views import set_language

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("challenge/", include("challenge.urls")),
    path("chart/", include("chart.urls")),
    path("admin_tools/", include("admin_tools.urls")),
    path("set/<str:language>/", set_language),
    path("bookstore/", include("bookstore.urls")),
    path("rosetta/", include("rosetta.urls")),
)

urlpatterns += (path("check_answer/", check_answer),)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
