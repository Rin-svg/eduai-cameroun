from django.urls import path
from . import views_admin_dashboard as views

app_name = 'admin_panel'

urlpatterns = [
    path('',                           views.dashboard,          name='dashboard'),
    path('utilisateurs/',              views.liste_utilisateurs, name='utilisateurs'),
    path('utilisateurs/creer/',        views.creer_utilisateur,  name='creer_utilisateur'),
    path('utilisateurs/<int:user_id>/toggle/', views.toggle_actif,   name='toggle_actif'),
    path('utilisateurs/<int:user_id>/reset/',  views.reset_password, name='reset_password'),
    path('epreuves/<int:epreuve_id>/valider/', views.valider_epreuve, name='valider_epreuve'),
    path('stats.json',                 views.stats_json,         name='stats_json'),
]
