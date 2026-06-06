#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EDUAI Cameroun - Fix encodage UTF-8 via Django ORM
Executer : Get-Content scripts\fix_encoding_orm.py | python manage.py shell
"""
import sys

# Forcer utf8mb4
from django.db import connection
with connection.cursor() as cur:
    cur.execute("SET NAMES utf8mb4")
    cur.execute("SET CHARACTER SET utf8mb4")

from apps.epreuves.models import Matiere, Niveau
from apps.quiz.models import Quiz

print(">>> Correction des matieres...")

corrections_matieres = {
    'MATH':  'Mathematiques',
    'FR':    'Francais',
    'PC':    'Physique-Chimie',
    'SVT':   'SVT',
    'HG':    'Histoire-Geographie',
    'PHILO': 'Philosophie',
    'INFO':  'Informatique',
    'ANG':   'Anglais',
    'ECO':   'Economie',
}

for code, nom in corrections_matieres.items():
    nb = Matiere.objects.filter(code=code).update(nom=nom)
    if nb:
        print(f"  OK : {code} -> {nom}")

print(">>> Correction des titres de quiz...")

corrections_quiz = [
    ('Math',        'Terminale',  'Quiz Mathematiques - Terminale',   'Revision sur les fonctions derivees et integrales.'),
    ('Physique',    'Terminale',  'Quiz Physique-Chimie - Terminale',  'Les lois de Newton et la mecanique du point.'),
    ('Fran',        '3',          'Quiz Francais - Grammaire 3eme',    'Accord du participe passe et conjugaison.'),
    ('Info',        'Licence',    'Quiz Informatique - Bases Python',  'Variables, boucles et fonctions en Python.'),
    ('SVT',         'Seconde',    'Quiz SVT - La cellule vivante',     'Structure et fonctionnement de la cellule eucaryote.'),
]

for titre_key, niveau_key, nouveau_titre, nouvelle_desc in corrections_quiz:
    quizzes = Quiz.objects.filter(titre__icontains=titre_key, niveau__nom__icontains=niveau_key)
    for q in quizzes:
        q.titre = nouveau_titre
        q.description = nouvelle_desc
        q.save()
        print(f"  OK : {q.titre}")

print("")
print("Matieres en base :")
for m in Matiere.objects.all():
    print(f"  [{m.code}] {m.nom}")

print("")
print("Quiz en base :")
for q in Quiz.objects.all():
    print(f"  - {q.titre} ({q.matiere.nom} / {q.niveau.nom})")

print("")
print("Correction terminee !")
