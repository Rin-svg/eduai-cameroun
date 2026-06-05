from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='monitoring_dashboard'),
    path('api/metriques/', views.api_metriques, name='api_metriques'),
    path('api/historique/', views.api_stats_historique, name='api_historique'),
    path('api/utilisateurs/', views.api_gestion_utilisateurs, name='api_utilisateurs'),
]
