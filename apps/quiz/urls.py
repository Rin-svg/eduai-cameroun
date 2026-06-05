from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_quiz, name='liste_quiz'),
    path('<int:pk>/demarrer/', views.demarrer_quiz, name='demarrer_quiz'),
    path('session/<int:session_id>/', views.passer_quiz, name='passer_quiz'),
    path('session/<int:session_id>/resultat/', views.resultat_quiz, name='resultat_quiz'),
    path('mes-resultats/', views.mes_resultats, name='mes_resultats'),
]
