from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.epreuves.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('epreuves/', include('apps.epreuves.urls')),
    path('quiz/', include('apps.quiz.urls')),
    path('ia/', include('apps.ia.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
    path('securite/', include('apps.securite.urls')),
    path('api/epreuves/', include('apps.epreuves.api_urls')),
    path('api/quiz/', include('apps.quiz.api_urls')),
    path('api/users/', include('apps.accounts.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "EDUAI Cameroun — Administration"
admin.site.site_title = "EDUAI Admin"
admin.site.index_title = "Panneau d'administration"
