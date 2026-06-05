"""
EDUAI Cameroun — Vues Sécurité & Alertes
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import TentativeConnexion, LogActivite, AlerteSecurite


def _admin_requis(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('connexion')
        if not (request.user.est_admin or request.user.is_superuser):
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('accueil')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@_admin_requis
def tableau_securite(request):
    alertes = AlerteSecurite.objects.filter(est_resolue=False).order_by('-date_alerte')[:20]
    ip_bloquees = TentativeConnexion.objects.filter(est_bloque=True).order_by('-derniere_tentative')
    logs = LogActivite.objects.select_related('utilisateur').order_by('-date_action')[:50]

    return render(request, 'securite/tableau.html', {
        'alertes': alertes,
        'ip_bloquees': ip_bloquees,
        'logs': logs,
        'nb_alertes': alertes.count(),
        'nb_ip_bloquees': ip_bloquees.count(),
    })


@login_required
@_admin_requis
def resoudre_alerte(request, pk):
    alerte = get_object_or_404(AlerteSecurite, pk=pk)
    alerte.est_resolue = True
    alerte.resolue_par = request.user
    alerte.save()
    messages.success(request, f"Alerte « {alerte.titre} » marquée comme résolue.")
    return redirect('tableau_securite')


@login_required
@_admin_requis
def debloquer_ip(request, pk):
    tentative = get_object_or_404(TentativeConnexion, pk=pk)
    tentative.est_bloque = False
    tentative.nb_tentatives = 0
    tentative.fin_blocage = None
    tentative.save()
    messages.success(request, f"IP {tentative.adresse_ip} débloquée avec succès.")
    return redirect('tableau_securite')


@login_required
@_admin_requis
def api_alertes(request):
    alertes = AlerteSecurite.objects.filter(est_resolue=False).order_by('-date_alerte')[:10]
    data = [
        {
            'id': a.pk,
            'niveau': a.niveau,
            'titre': a.titre,
            'message': a.message,
            'ip': a.adresse_ip,
            'date': a.date_alerte.strftime('%d/%m/%Y %H:%M'),
        }
        for a in alertes
    ]
    return JsonResponse({'alertes': data, 'total': len(data)})
