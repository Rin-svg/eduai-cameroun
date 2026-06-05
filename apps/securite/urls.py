from django.urls import path
from . import views

urlpatterns = [
    path('', views.tableau_securite, name='tableau_securite'),
    path('alerte/<int:pk>/resoudre/', views.resoudre_alerte, name='resoudre_alerte'),
    path('ip/<int:pk>/debloquer/', views.debloquer_ip, name='debloquer_ip'),
    path('api/alertes/', views.api_alertes, name='api_alertes'),
]
