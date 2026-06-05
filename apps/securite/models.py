"""
EDUAI Cameroun — Modèles Sécurité & Journalisation
"""
from django.db import models
from django.conf import settings


class TentativeConnexion(models.Model):
    adresse_ip = models.GenericIPAddressField(verbose_name="Adresse IP")
    username = models.CharField(max_length=150, blank=True)
    nb_tentatives = models.PositiveIntegerField(default=1)
    premiere_tentative = models.DateTimeField(auto_now_add=True)
    derniere_tentative = models.DateTimeField(auto_now=True)
    est_bloque = models.BooleanField(default=False)
    fin_blocage = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Tentative de connexion"
        verbose_name_plural = "Tentatives de connexion"
        ordering = ['-derniere_tentative']

    def __str__(self):
        statut = "🔒 BLOQUÉ" if self.est_bloque else f"{self.nb_tentatives} tentative(s)"
        return f"{self.adresse_ip} — {statut}"


class LogActivite(models.Model):
    TYPE_ACTIONS = [
        ('connexion', 'Connexion'),
        ('deconnexion', 'Déconnexion'),
        ('telechargement', 'Téléchargement'),
        ('upload', 'Upload épreuve'),
        ('quiz', 'Passage quiz'),
        ('ia', 'Requête IA'),
        ('admin', 'Action admin'),
        ('alerte', 'Alerte sécurité'),
    ]
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    type_action = models.CharField(max_length=30, choices=TYPE_ACTIONS)
    description = models.TextField()
    adresse_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    date_action = models.DateTimeField(auto_now_add=True)
    est_suspect = models.BooleanField(default=False)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Log d'activité"
        verbose_name_plural = "Logs d'activité"
        ordering = ['-date_action']

    def __str__(self):
        user = self.utilisateur or f"IP:{self.adresse_ip}"
        return f"{user} — {self.get_type_action_display()} — {self.date_action.strftime('%d/%m %H:%M')}"


class AlerteSecurite(models.Model):
    NIVEAUX = [
        ('info', 'Information'),
        ('avertissement', 'Avertissement'),
        ('critique', 'Critique'),
    ]
    niveau = models.CharField(max_length=20, choices=NIVEAUX, default='avertissement')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    date_alerte = models.DateTimeField(auto_now_add=True)
    est_resolue = models.BooleanField(default=False)
    resolue_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Alerte de sécurité"
        verbose_name_plural = "Alertes de sécurité"
        ordering = ['-date_alerte']

    def __str__(self):
        return f"[{self.get_niveau_display()}] {self.titre}"
