"""
EDUAI Cameroun — Modèles Quiz Interactif
"""
from django.db import models
from django.conf import settings
from apps.epreuves.models import Matiere, Niveau


class Quiz(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    duree_minutes = models.PositiveIntegerField(default=30, verbose_name="Durée (minutes)")
    cree_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)
    nb_tentatives_max = models.PositiveIntegerField(default=3)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre

    @property
    def nb_questions(self):
        return self.questions.count()

    @property
    def score_total(self):
        return self.questions.aggregate(total=models.Sum('points'))['total'] or 0


class Question(models.Model):
    TYPES = [
        ('qcm', 'Choix Multiple (QCM)'),
        ('vrai_faux', 'Vrai / Faux'),
        ('texte', 'Réponse Texte'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    enonce = models.TextField(verbose_name="Énoncé")
    type_question = models.CharField(max_length=20, choices=TYPES, default='qcm')
    points = models.PositiveIntegerField(default=1)
    explication = models.TextField(blank=True, verbose_name="Explication de la réponse")
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"Q{self.ordre}: {self.enonce[:60]}..."


class Choix(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=500)
    est_correct = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"{'✓' if self.est_correct else '✗'} {self.texte}"


class SessionQuiz(models.Model):
    STATUTS = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('abandonne', 'Abandonné'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    score_obtenu = models.FloatField(default=0)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Session Quiz"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.utilisateur} — {self.quiz} ({self.score_obtenu}pts)"

    @property
    def pourcentage(self):
        total = self.quiz.score_total
        if total == 0:
            return 0
        return round((self.score_obtenu / total) * 100, 1)


class ReponseEleve(models.Model):
    session = models.ForeignKey(SessionQuiz, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choix_selectionne = models.ForeignKey(Choix, on_delete=models.SET_NULL, null=True, blank=True)
    texte_reponse = models.TextField(blank=True)
    est_correcte = models.BooleanField(default=False)
    points_obtenus = models.FloatField(default=0)
