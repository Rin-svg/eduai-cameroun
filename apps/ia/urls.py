from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil_ia, name='accueil_ia'),
    path('corriger/', views.corriger_reponse, name='corriger_reponse'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('plagiat/', views.detecter_plagiat, name='detecter_plagiat'),
    path('generer-quiz/', views.generer_quiz, name='generer_quiz'),
]
