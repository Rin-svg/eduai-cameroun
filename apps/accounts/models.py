"""
EDUAI Cameroun — Modèle Utilisateur
Rôles : admin, enseignant, eleve
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('enseignant', 'Enseignant'),
        ('eleve', 'Élève'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='eleve', verbose_name="Rôle")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    classe = models.CharField(max_length=50, blank=True, verbose_name="Classe / Filière")
    etablissement = models.CharField(max_length=100, blank=True, verbose_name="Établissement")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Photo de profil")
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_activite = models.DateTimeField(auto_now=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dernière IP")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def est_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def est_enseignant(self):
        return self.role == 'enseignant'

    @property
    def est_eleve(self):
        return self.role == 'eleve'
