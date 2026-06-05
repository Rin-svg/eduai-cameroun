"""
EDUAI Cameroun — Modèles Épreuves
"""
from django.db import models
from django.conf import settings


class Matiere(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Matière")
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, default='book', verbose_name="Icône Bootstrap")

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Niveau(models.Model):
    CYCLES = [
        ('primaire', 'Primaire'),
        ('college', 'Collège'),
        ('lycee', 'Lycée'),
        ('superieur', 'Supérieur'),
    ]
    nom = models.CharField(max_length=50, verbose_name="Niveau")
    cycle = models.CharField(max_length=20, choices=CYCLES)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Niveau"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.nom} ({self.get_cycle_display()})"


class Epreuve(models.Model):
    TYPES_EXAMEN = [
        ('baccalaureat', 'Baccalauréat'),
        ('bepc', 'BEPC'),
        ('probatoire', 'Probatoire'),
        ('concours', 'Concours'),
        ('ds', 'Devoir Surveillé'),
        ('examen_final', 'Examen Final'),
        ('entrainement', 'Entraînement'),
    ]
    titre = models.CharField(max_length=200, verbose_name="Titre de l'épreuve")
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='epreuves')
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='epreuves')
    type_examen = models.CharField(max_length=30, choices=TYPES_EXAMEN, verbose_name="Type d'examen")
    annee = models.PositiveIntegerField(verbose_name="Année")
    fichier = models.FileField(upload_to='epreuves/%Y/', verbose_name="Fichier (PDF/DOC)")
    corrige = models.FileField(upload_to='epreuves/corriges/%Y/', blank=True, null=True, verbose_name="Corrigé (optionnel)")
    description = models.TextField(blank=True)
    uploade_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='epreuves_uploadees')
    date_upload = models.DateTimeField(auto_now_add=True)
    nb_telechargements = models.PositiveIntegerField(default=0, verbose_name="Téléchargements")
    est_valide = models.BooleanField(default=True, verbose_name="Validé")

    class Meta:
        verbose_name = "Épreuve"
        verbose_name_plural = "Épreuves"
        ordering = ['-annee', '-date_upload']

    def __str__(self):
        return f"{self.titre} — {self.matiere} {self.annee}"


class Telechargement(models.Model):
    epreuve = models.ForeignKey(Epreuve, on_delete=models.CASCADE, related_name='telechargements')
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    adresse_ip = models.GenericIPAddressField()
    date_telechargement = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Téléchargement"
        ordering = ['-date_telechargement']
