from django.contrib import admin
from .models import TentativeConnexion, LogActivite, AlerteSecurite

@admin.register(TentativeConnexion)
class TentativeAdmin(admin.ModelAdmin):
    list_display = ['adresse_ip', 'username', 'nb_tentatives', 'est_bloque', 'fin_blocage', 'derniere_tentative']
    list_filter = ['est_bloque']
    search_fields = ['adresse_ip', 'username']
    readonly_fields = ['premiere_tentative', 'derniere_tentative']

@admin.register(LogActivite)
class LogActiviteAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'type_action', 'adresse_ip', 'date_action', 'est_suspect']
    list_filter = ['type_action', 'est_suspect', 'date_action']
    search_fields = ['description', 'adresse_ip']
    readonly_fields = ['date_action']

@admin.register(AlerteSecurite)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'niveau', 'adresse_ip', 'date_alerte', 'est_resolue']
    list_filter = ['niveau', 'est_resolue']
    readonly_fields = ['date_alerte']
    actions = ['marquer_resolues']

    def marquer_resolues(self, request, queryset):
        queryset.update(est_resolue=True, resolue_par=request.user)
    marquer_resolues.short_description = "Marquer les alertes sélectionnées comme résolues"
