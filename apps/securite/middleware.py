"""
EDUAI Cameroun — Middleware de Sécurité
Détection brute force + journalisation automatique
"""
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.conf import settings
from datetime import timedelta
import threading

_lock = threading.Lock()


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class BruteForceMiddleware:
    """
    Bloque automatiquement une IP après MAX_LOGIN_ATTEMPTS échecs.
    Durée de blocage : LOCKOUT_DURATION_MINUTES minutes.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/accounts/connexion/' and request.method == 'POST':
            ip = get_client_ip(request)
            if self._est_bloque(ip):
                return HttpResponseForbidden(
                    "<h1>Accès temporairement bloqué</h1>"
                    "<p>Trop de tentatives de connexion. Réessayez dans 15 minutes.</p>"
                    "<p><a href='/'>Retour à l'accueil</a></p>"
                )
        response = self.get_response(request)
        return response

    def _est_bloque(self, ip):
        try:
            from apps.securite.models import TentativeConnexion
            tentative = TentativeConnexion.objects.filter(adresse_ip=ip, est_bloque=True).first()
            if tentative and tentative.fin_blocage:
                if timezone.now() < tentative.fin_blocage:
                    return True
                else:
                    tentative.est_bloque = False
                    tentative.nb_tentatives = 0
                    tentative.save()
        except Exception:
            pass
        return False


class ActivityLogMiddleware:
    """
    Journal automatique des actions importantes.
    """
    ACTIONS_A_JOURNALISER = [
        '/accounts/connexion/',
        '/accounts/deconnexion/',
        '/epreuves/telecharger/',
        '/epreuves/upload/',
        '/ia/',
        '/quiz/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._journaliser(request, response)
        except Exception:
            pass
        return response

    def _journaliser(self, request, response):
        from apps.securite.models import LogActivite
        path = request.path
        methode = request.method

        type_action = None
        if '/connexion/' in path and methode == 'POST' and response.status_code in [200, 302]:
            type_action = 'connexion'
        elif '/deconnexion/' in path:
            type_action = 'deconnexion'
        elif '/telecharger/' in path:
            type_action = 'telechargement'
        elif '/upload/' in path and methode == 'POST':
            type_action = 'upload'
        elif '/ia/' in path and methode == 'POST':
            type_action = 'ia'

        if type_action:
            utilisateur = request.user if request.user.is_authenticated else None
            LogActivite.objects.create(
                utilisateur=utilisateur,
                type_action=type_action,
                description=f"{methode} {path}",
                adresse_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
