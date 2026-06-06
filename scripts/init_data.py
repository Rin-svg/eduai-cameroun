#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EDUAI Cameroun — Script d'initialisation des données de démonstration
Exécuter : python manage.py shell < scripts/init_data.py
Version 1.1 — Fix encodage + données enrichies (plusieurs quiz)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduai_cameroun.settings')
django.setup()

# ── Forcer utf8mb4 sur la connexion MySQL ────────────────────────────────────
from django.db import connection
with connection.cursor() as cur:
    cur.execute("SET NAMES utf8mb4")
    cur.execute("SET CHARACTER SET utf8mb4")

from apps.epreuves.models import Matiere, Niveau
from apps.accounts.models import Utilisateur
from apps.quiz.models import Quiz, Question, Choix

# ── Matières ─────────────────────────────────────────────────────────────────
print(">>> Création des matières...")
matieres_data = [
    ('Mathématiques',       'MATH',  'calculator'),
    ('Français',            'FR',    'book'),
    ('Physique-Chimie',     'PC',    'lightning'),
    ('SVT',                 'SVT',   'tree'),
    ('Histoire-Géographie', 'HG',    'globe'),
    ('Philosophie',         'PHILO', 'brain'),
    ('Informatique',        'INFO',  'laptop'),
    ('Anglais',             'ANG',   'translate'),
    ('Économie',            'ECO',   'currency-exchange'),
]
for nom, code, icone in matieres_data:
    obj, created = Matiere.objects.get_or_create(code=code, defaults={'nom': nom, 'icone': icone})
    if not created and obj.nom != nom:          # corriger encodage existant
        obj.nom = nom
        obj.save()
print(f"  {Matiere.objects.count()} matières OK.")

# ── Niveaux ──────────────────────────────────────────────────────────────────
print(">>> Création des niveaux...")
niveaux_data = [
    ('6ème',      'college',   1), ('5ème',    'college',   2),
    ('4ème',      'college',   3), ('3ème',    'college',   4),
    ('Seconde',   'lycee',     5), ('Première','lycee',     6),
    ('Terminale', 'lycee',     7),
    ('Licence 1', 'superieur', 8), ('Licence 2','superieur',9),
    ('Licence 3', 'superieur',10),
]
for nom, cycle, ordre in niveaux_data:
    Niveau.objects.get_or_create(nom=nom, defaults={'cycle': cycle, 'ordre': ordre})
print(f"  {Niveau.objects.count()} niveaux OK.")

# ── Comptes ──────────────────────────────────────────────────────────────────
print(">>> Création des comptes...")
if not Utilisateur.objects.filter(username='admin').exists():
    Utilisateur.objects.create_superuser(
        username='admin', email='admin@eduai.cm', password='EduAI2025!',
        first_name='Admin', last_name='EDUAI', role='admin',
    )
    print("  admin / EduAI2025! créé")

comptes = [
    ('enseignant1', 'Paul',  'Martin', 'enseignant', 'Terminale A',  'Lycée de Yaoundé'),
    ('eleve1',      'Jean',  'Dupont', 'eleve',      'Terminale D',  'Lycée Général Leclerc'),
    ('eleve2',      'Marie', 'Nkomo',  'eleve',      '3ème',         'Collège de la Retraite'),
    ('eleve3',      'Simon', 'Ottou',  'eleve',      'Terminale C',  'Lycée Bilingue de Bafoussam'),
]
for username, prenom, nom, role, classe, etab in comptes:
    if not Utilisateur.objects.filter(username=username).exists():
        Utilisateur.objects.create_user(
            username=username, password='EduAI2025!',
            first_name=prenom, last_name=nom, role=role,
            classe=classe, etablissement=etab,
        )
        print(f"  {username} / EduAI2025! créé")

admin_user = Utilisateur.objects.filter(username='admin').first()
enseignant  = Utilisateur.objects.filter(username='enseignant1').first()

# ── Quiz de démonstration ────────────────────────────────────────────────────
print(">>> Création des quiz de démonstration...")

def creer_quiz(titre, description, code_matiere, nom_niveau, duree, createur, questions_data):
    matiere = Matiere.objects.filter(code=code_matiere).first()
    niveau  = Niveau.objects.filter(nom=nom_niveau).first()
    if not matiere or not niveau:
        print(f"  ⚠ Matière/niveau introuvable pour : {titre}")
        return
    if Quiz.objects.filter(titre=titre).exists():
        print(f"  → déjà existant : {titre}")
        return
    quiz = Quiz.objects.create(
        titre=titre, description=description,
        matiere=matiere, niveau=niveau,
        duree_minutes=duree, cree_par=createur, est_actif=True,
    )
    for q_data in questions_data:
        q = Question.objects.create(
            quiz=quiz,
            enonce=q_data['enonce'],
            type_question=q_data.get('type', 'qcm'),
            points=q_data.get('points', 1),
            ordre=q_data.get('ordre', 1),
            explication=q_data.get('explication', ''),
        )
        for i, (texte, correct) in enumerate(q_data['choix'], 1):
            Choix.objects.create(question=q, texte=texte, est_correct=correct, ordre=i)
    print(f"  ✓ {titre}")

# ── Quiz 1 : Maths Terminale ─────────────────────────────────────────────────
creer_quiz(
    titre       = 'Quiz Mathématiques — Terminale',
    description = 'Révision sur les fonctions dérivées et intégrales.',
    code_matiere= 'MATH', nom_niveau='Terminale', duree=20, createur=admin_user,
    questions_data=[
        {
            'enonce': "Quelle est la dérivée de f(x) = x² + 3x + 2 ?",
            'type': 'qcm', 'points': 2, 'ordre': 1,
            'choix': [
                ("f'(x) = 2x + 3", True),
                ("f'(x) = x + 3",  False),
                ("f'(x) = 2x",     False),
                ("f'(x) = 3x + 2", False),
            ]
        },
        {
            'enonce': "L'intégrale de f(x) = 2x est x² + C.",
            'type': 'vrai_faux', 'points': 1, 'ordre': 2,
            'explication': "La primitive de 2x est x² + C (vérifiable par dérivation).",
            'choix': [("Vrai", True), ("Faux", False)]
        },
        {
            'enonce': "Quelle est la limite de (sin x)/x quand x tend vers 0 ?",
            'type': 'qcm', 'points': 2, 'ordre': 3,
            'explication': "C'est une limite remarquable fondamentale.",
            'choix': [
                ("0",   False),
                ("1",   True),
                ("∞",   False),
                ("−1",  False),
            ]
        },
    ]
)

# ── Quiz 2 : Physique-Chimie Terminale ───────────────────────────────────────
creer_quiz(
    titre       = 'Quiz Physique-Chimie — Terminale',
    description = 'Les lois de Newton et la mécanique du point.',
    code_matiere= 'PC', nom_niveau='Terminale', duree=25, createur=enseignant,
    questions_data=[
        {
            'enonce': "Quelle est l'unité du Newton (N) en unités de base SI ?",
            'type': 'qcm', 'points': 2, 'ordre': 1,
            'choix': [
                ("kg·m·s⁻²",  True),
                ("kg·m²·s⁻¹", False),
                ("m·s⁻²",     False),
                ("kg·s⁻²",    False),
            ]
        },
        {
            'enonce': "La 3ème loi de Newton est la loi d'action-réaction.",
            'type': 'vrai_faux', 'points': 1, 'ordre': 2,
            'explication': "Toute force exercée par A sur B est opposée à la force exercée par B sur A.",
            'choix': [("Vrai", True), ("Faux", False)]
        },
        {
            'enonce': "Quelle formule relie force, masse et accélération ?",
            'type': 'qcm', 'points': 2, 'ordre': 3,
            'choix': [
                ("F = m × a",  True),
                ("F = m / a",  False),
                ("F = a / m",  False),
                ("F = m + a",  False),
            ]
        },
        {
            'enonce': "L'énergie cinétique d'un objet de masse m à la vitesse v est ½mv².",
            'type': 'vrai_faux', 'points': 1, 'ordre': 4,
            'explication': "Ec = ½mv² est la formule standard de l'énergie cinétique.",
            'choix': [("Vrai", True), ("Faux", False)]
        },
    ]
)

# ── Quiz 3 : Français — 3ème ─────────────────────────────────────────────────
creer_quiz(
    titre       = 'Quiz Français — Grammaire 3ème',
    description = 'Accord du participe passé et conjugaison.',
    code_matiere= 'FR', nom_niveau='3ème', duree=15, createur=enseignant,
    questions_data=[
        {
            'enonce': "Le participe passé employé avec 'avoir' s'accorde avec le sujet.",
            'type': 'vrai_faux', 'points': 1, 'ordre': 1,
            'explication': "Avec 'avoir', le participe s'accorde avec le COD si celui-ci est placé AVANT.",
            'choix': [("Vrai", False), ("Faux", True)]
        },
        {
            'enonce': "Quel est le mode du verbe dans : 'Bien qu'il soit fatigué...' ?",
            'type': 'qcm', 'points': 2, 'ordre': 2,
            'choix': [
                ("Subjonctif", True),
                ("Indicatif",  False),
                ("Conditionnel", False),
                ("Infinitif",  False),
            ]
        },
        {
            'enonce': "La phrase 'Le chat mange la souris' est une phrase :",
            'type': 'qcm', 'points': 1, 'ordre': 3,
            'choix': [
                ("Simple et active",   True),
                ("Simple et passive",  False),
                ("Complexe",          False),
                ("Nominale",          False),
            ]
        },
    ]
)

# ── Quiz 4 : Informatique — Licence 1 ────────────────────────────────────────
creer_quiz(
    titre       = 'Quiz Informatique — Bases Python',
    description = 'Variables, boucles et fonctions en Python.',
    code_matiere= 'INFO', nom_niveau='Licence 1', duree=30, createur=admin_user,
    questions_data=[
        {
            'enonce': "Quelle instruction permet d'afficher du texte en Python ?",
            'type': 'qcm', 'points': 1, 'ordre': 1,
            'choix': [
                ("print()",   True),
                ("echo()",    False),
                ("display()", False),
                ("write()",   False),
            ]
        },
        {
            'enonce': "Quelle est la valeur de : len([1, 2, 3, 4, 5]) ?",
            'type': 'qcm', 'points': 1, 'ordre': 2,
            'choix': [
                ("5",  True),
                ("4",  False),
                ("6",  False),
                ("0",  False),
            ]
        },
        {
            'enonce': "En Python, les indices de liste commencent à 0.",
            'type': 'vrai_faux', 'points': 1, 'ordre': 3,
            'explication': "L'indice 0 correspond au premier élément de la liste.",
            'choix': [("Vrai", True), ("Faux", False)]
        },
        {
            'enonce': "Quel mot-clé définit une fonction en Python ?",
            'type': 'qcm', 'points': 2, 'ordre': 4,
            'choix': [
                ("def",      True),
                ("function", False),
                ("func",     False),
                ("define",   False),
            ]
        },
        {
            'enonce': "Quelle boucle s'exécute TANT QU'une condition est vraie ?",
            'type': 'qcm', 'points': 1, 'ordre': 5,
            'choix': [
                ("while", True),
                ("for",   False),
                ("do",    False),
                ("loop",  False),
            ]
        },
    ]
)

# ── Quiz 5 : SVT — Seconde ───────────────────────────────────────────────────
creer_quiz(
    titre       = 'Quiz SVT — La cellule vivante',
    description = 'Structure et fonctionnement de la cellule eucaryote.',
    code_matiere= 'SVT', nom_niveau='Seconde', duree=20, createur=enseignant,
    questions_data=[
        {
            'enonce': "Quel organite est le 'centre énergétique' de la cellule eucaryote ?",
            'type': 'qcm', 'points': 2, 'ordre': 1,
            'explication': "La mitochondrie réalise la respiration cellulaire et produit de l'ATP.",
            'choix': [
                ("Mitochondrie", True),
                ("Ribosome",     False),
                ("Noyau",        False),
                ("Vacuole",      False),
            ]
        },
        {
            'enonce': "L'ADN se trouve uniquement dans le noyau de la cellule eucaryote.",
            'type': 'vrai_faux', 'points': 1, 'ordre': 2,
            'explication': "On trouve aussi de l'ADN dans les mitochondries et les chloroplastes.",
            'choix': [("Vrai", False), ("Faux", True)]
        },
        {
            'enonce': "Quelle membrane entoure toute cellule animale ?",
            'type': 'qcm', 'points': 1, 'ordre': 3,
            'choix': [
                ("Membrane plasmique", True),
                ("Paroi cellulaire",   False),
                ("Membrane nucléaire", False),
                ("Réticulum",         False),
            ]
        },
    ]
)

print(f"\n✅ Initialisation terminée !")
print(f"   {Quiz.objects.count()} quiz disponibles")
print(f"   Quiz actifs : {Quiz.objects.filter(est_actif=True).count()}")
print(f"\n   Comptes :")
print(f"   Admin      : admin / EduAI2025!")
print(f"   Enseignant : enseignant1 / EduAI2025!")
print(f"   Élève      : eleve1, eleve2, eleve3 / EduAI2025!")
print(f"\n   URL : http://192.168.1.10:8000")
