from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('liste/', views.liste_epreuves, name='liste_epreuves'),
    path('<int:pk>/', views.detail_epreuve, name='detail_epreuve'),
    path('<int:pk>/telecharger/', views.telecharger_epreuve, name='telecharger_epreuve'),
    path('upload/', views.upload_epreuve, name='upload_epreuve'),
]
