from django.contrib import admin
from .models import Matiere, Niveau, Epreuve, Telechargement

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code']
    search_fields = ['nom', 'code']

@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ['nom', 'cycle', 'ordre']
    list_editable = ['ordre']

@admin.register(Epreuve)
class EpreuveAdmin(admin.ModelAdmin):
    list_display = ['titre', 'matiere', 'niveau', 'type_examen', 'annee', 'nb_telechargements', 'uploade_par', 'est_valide']
    list_filter = ['matiere', 'niveau', 'type_examen', 'est_valide']
    search_fields = ['titre', 'description']
    list_editable = ['est_valide']
    date_hierarchy = 'date_upload'

@admin.register(Telechargement)
class TelechargementAdmin(admin.ModelAdmin):
    list_display = ['epreuve', 'utilisateur', 'adresse_ip', 'date_telechargement']
    list_filter = ['date_telechargement']
    readonly_fields = ['date_telechargement']
