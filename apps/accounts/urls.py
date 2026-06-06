from django.urls import path
from . import views

urlpatterns = [
    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/', views.profil, name='profil'),
    path('inscription/', views.inscription, name='inscription'),
    path('inscription/eleve/', views.inscription_eleve, name='inscription_eleve'),
    path('inscription/enseignant/', views.inscription_enseignant, name='inscription_enseignant'),
]
