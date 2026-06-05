from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'role', 'email', 'adresse_ip', 'derniere_activite', 'is_active']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations EDUAI', {'fields': ('role', 'telephone', 'classe', 'etablissement', 'avatar', 'adresse_ip')}),
    )
