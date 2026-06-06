"""
EDUAI Cameroun — Filtres de template personnalisés pour l'app Quiz
"""
import builtins
from django import template

register = template.Library()


@register.filter
def chr(value):
    """
    Convertit un entier en caractère Unicode.
    Utilisé pour afficher les lettres des choix : 65→A, 66→B, 67→C...
    Exemple : {{ forloop.counter|add:64|chr }} → A, B, C, D...
    """
    try:
        return builtins.chr(int(value))
    except (TypeError, ValueError):
        return ''
