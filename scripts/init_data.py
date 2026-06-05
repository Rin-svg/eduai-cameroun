#!/usr/bin/env python
"""
EDUAI Cameroun — Script d'initialisation des données de démonstration
Exécuter : python manage.py shell < scripts/init_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduai_cameroun.settings')
django.setup()

from apps.epreuves.models import Matiere, Niveau
from apps.accounts.models import Utilisateur
from apps.quiz.models import Quiz, Question, Choix

print(">>> Création des matières...")
matieres_data = [
    ('Mathématiques', 'MATH', 'calculator'),
    ('Français', 'FR', 'book'),
    ('Physique-Chimie', 'PC', 'lightning'),
    ('SVT', 'SVT', 'tree'),
    ('Histoire-Géographie', 'HG', 'globe'),
    ('Philosophie', 'PHILO', 'brain'),
    ('Informatique', 'INFO', 'laptop'),
    ('Anglais', 'ANG', 'translate'),
    ('Économie', 'ECO', 'currency-exchange'),
]
for nom, code, icone in matieres_data:
    Matiere.objects.get_or_create(code=code, defaults={'nom': nom, 'icone': icone})
print(f"  {Matiere.objects.count()} matières créées.")

print(">>> Création des niveaux...")
niveaux_data = [
    ('6ème', 'college', 1), ('5ème', 'college', 2), ('4ème', 'college', 3), ('3ème', 'college', 4),
    ('Seconde', 'lycee', 5), ('Première', 'lycee', 6), ('Terminale', 'lycee', 7),
    ('Licence 1', 'superieur', 8), ('Licence 2', 'superieur', 9), ('Licence 3', 'superieur', 10),
]
for nom, cycle, ordre in niveaux_data:
    Niveau.objects.get_or_create(nom=nom, defaults={'cycle': cycle, 'ordre': ordre})
print(f"  {Niveau.objects.count()} niveaux créés.")

print(">>> Création du compte administrateur...")
if not Utilisateur.objects.filter(username='admin').exists():
    admin = Utilisateur.objects.create_superuser(
        username='admin',
        email='admin@eduai.cm',
        password='EduAI2025!',
        first_name='Admin',
        last_name='EDUAI',
        role='admin',
    )
    print("  Admin créé : admin / EduAI2025!")
else:
    print("  Admin déjà existant.")

print(">>> Création des comptes de démonstration...")
comptes = [
    ('enseignant1', 'Prof', 'Martin', 'enseignant', 'Terminale A', 'Lycée de Yaoundé'),
    ('eleve1', 'Jean', 'Dupont', 'eleve', 'Terminale D', 'Lycée Général Leclerc'),
    ('eleve2', 'Marie', 'Nkomo', 'eleve', '3ème', 'Collège de la Retraite'),
]
for username, prenom, nom, role, classe, etab in comptes:
    if not Utilisateur.objects.filter(username=username).exists():
        Utilisateur.objects.create_user(
            username=username, password='EduAI2025!',
            first_name=prenom, last_name=nom, role=role,
            classe=classe, etablissement=etab
        )
        print(f"  Compte créé : {username} / EduAI2025!")

print(">>> Création d'un quiz de démonstration...")
math = Matiere.objects.filter(code='MATH').first()
terminale = Niveau.objects.filter(nom='Terminale').first()
admin_user = Utilisateur.objects.filter(username='admin').first()

if math and terminale and not Quiz.objects.filter(titre='Quiz Mathématiques — Terminale').exists():
    quiz = Quiz.objects.create(
        titre='Quiz Mathématiques — Terminale',
        description='Quiz de révision sur les fonctions dérivées et intégrales.',
        matiere=math, niveau=terminale,
        duree_minutes=20, cree_par=admin_user, est_actif=True,
    )
    q1 = Question.objects.create(quiz=quiz, enonce='Quelle est la dérivée de f(x) = x² + 3x + 2 ?', type_question='qcm', points=2, ordre=1)
    Choix.objects.create(question=q1, texte='f\'(x) = 2x + 3', est_correct=True, ordre=1)
    Choix.objects.create(question=q1, texte='f\'(x) = x + 3', est_correct=False, ordre=2)
    Choix.objects.create(question=q1, texte='f\'(x) = 2x', est_correct=False, ordre=3)
    Choix.objects.create(question=q1, texte='f\'(x) = 3x + 2', est_correct=False, ordre=4)

    q2 = Question.objects.create(quiz=quiz, enonce='L\'intégrale de f(x) = 2x est x² + C.', type_question='vrai_faux', points=1, ordre=2, explication='En effet, la primitive de 2x est x² + C.')
    Choix.objects.create(question=q2, texte='Vrai', est_correct=True, ordre=1)
    Choix.objects.create(question=q2, texte='Faux', est_correct=False, ordre=2)

    print("  Quiz de démonstration créé.")

print("\n✅ Initialisation terminée ! Accédez à http://192.168.1.10")
print("   Admin : admin / EduAI2025!")
print("   Enseignant : enseignant1 / EduAI2025!")
print("   Élève : eleve1 / EduAI2025!")
