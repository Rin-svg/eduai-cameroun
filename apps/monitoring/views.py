"""
EDUAI Cameroun — Dashboard Monitoring Temps Réel
CPU, RAM, Disque, Réseau, Sessions, BDD, Logs IA
Compatible Windows 11 via psutil
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import psutil
import platform
import json

User = get_user_model()


def _admin_requis(view_func):
    from functools import wraps
    from django.shortcuts import redirect
    from django.contrib import messages
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
def dashboard(request):
    """Tableau de bord principal de monitoring"""
    return render(request, 'monitoring/dashboard.html')


@login_required
@_admin_requis
def api_metriques(request):
    """API JSON — métriques système en temps réel via psutil"""
    try:
        # CPU & RAM
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count()
        ram = psutil.virtual_memory()
        disque = psutil.disk_usage('/')

        # Réseau
        net = psutil.net_io_counters()

        # Système
        boot_time = psutil.boot_time()
        uptime_sec = (timezone.now().timestamp() - boot_time)
        uptime_h = int(uptime_sec // 3600)
        uptime_m = int((uptime_sec % 3600) // 60)

        # Processus
        nb_processus = len(psutil.pids())

        # Données applicatives
        now = timezone.now()
        dernieres_15min = now - timedelta(minutes=15)

        from apps.securite.models import LogActivite, AlerteSecurite
        from apps.epreuves.models import Telechargement

        # Sessions actives (utilisateurs connectés dans les 15 dernières minutes)
        sessions_actives = User.objects.filter(derniere_activite__gte=dernieres_15min)
        utilisateurs_connectes = list(sessions_actives.values(
            'id', 'username', 'first_name', 'last_name', 'role', 'adresse_ip', 'derniere_activite'
        )[:20])
        for u in utilisateurs_connectes:
            if u['derniere_activite']:
                u['derniere_activite'] = u['derniere_activite'].strftime('%H:%M:%S')

        # Logs récents
        logs_recents = list(LogActivite.objects.select_related('utilisateur').order_by('-date_action')[:10].values(
            'type_action', 'description', 'adresse_ip', 'date_action', 'est_suspect'
        ))
        for log in logs_recents:
            log['date_action'] = log['date_action'].strftime('%H:%M:%S')

        # Alertes non résolues
        alertes = list(AlerteSecurite.objects.filter(est_resolue=False).order_by('-date_alerte')[:5].values(
            'niveau', 'titre', 'message', 'adresse_ip', 'date_alerte'
        ))
        for a in alertes:
            a['date_alerte'] = a['date_alerte'].strftime('%d/%m %H:%M')

        # Téléchargements (24h)
        tele_24h = Telechargement.objects.filter(
            date_telechargement__gte=now - timedelta(hours=24)
        ).count()

        # Stats IA (1h)
        ia_1h = LogActivite.objects.filter(
            type_action='ia', date_action__gte=now - timedelta(hours=1)
        ).count()

        return JsonResponse({
            'systeme': {
                'os': platform.system() + ' ' + platform.release(),
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'ram_total_gb': round(ram.total / (1024**3), 1),
                'ram_utilise_gb': round(ram.used / (1024**3), 1),
                'ram_percent': ram.percent,
                'disque_total_gb': round(disque.total / (1024**3), 1),
                'disque_utilise_gb': round(disque.used / (1024**3), 1),
                'disque_percent': disque.percent,
                'uptime': f"{uptime_h}h {uptime_m}min",
                'nb_processus': nb_processus,
                'net_envoye_mb': round(net.bytes_sent / (1024**2), 1),
                'net_recu_mb': round(net.bytes_recv / (1024**2), 1),
            },
            'application': {
                'nb_utilisateurs_total': User.objects.count(),
                'nb_sessions_actives': sessions_actives.count(),
                'nb_telechargements_24h': tele_24h,
                'nb_requetes_ia_1h': ia_1h,
                'nb_alertes_actives': AlerteSecurite.objects.filter(est_resolue=False).count(),
            },
            'utilisateurs_connectes': utilisateurs_connectes,
            'logs_recents': logs_recents,
            'alertes': alertes,
            'timestamp': now.strftime('%H:%M:%S'),
        })
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=500)


@login_required
@_admin_requis
def api_stats_historique(request):
    """Statistiques historiques pour les graphiques"""
    from apps.epreuves.models import Telechargement, Epreuve
    from apps.quiz.models import SessionQuiz
    from apps.securite.models import LogActivite

    now = timezone.now()
    # Téléchargements par heure (12 dernières heures)
    telechargements_par_heure = []
    for i in range(12, -1, -1):
        debut = now - timedelta(hours=i+1)
        fin = now - timedelta(hours=i)
        nb = Telechargement.objects.filter(date_telechargement__gte=debut, date_telechargement__lt=fin).count()
        telechargements_par_heure.append({
            'heure': fin.strftime('%H:00'),
            'nb': nb,
        })

    # Quiz par jour (7 derniers jours)
    quiz_par_jour = []
    for i in range(6, -1, -1):
        jour = now.date() - timedelta(days=i)
        nb = SessionQuiz.objects.filter(date_debut__date=jour, statut='termine').count()
        quiz_par_jour.append({'jour': jour.strftime('%d/%m'), 'nb': nb})

    # Requêtes IA par heure (8 dernières heures)
    ia_par_heure = []
    for i in range(8, -1, -1):
        debut = now - timedelta(hours=i+1)
        fin = now - timedelta(hours=i)
        nb = LogActivite.objects.filter(type_action='ia', date_action__gte=debut, date_action__lt=fin).count()
        ia_par_heure.append({'heure': fin.strftime('%H:00'), 'nb': nb})

    return JsonResponse({
        'telechargements_par_heure': telechargements_par_heure,
        'quiz_par_jour': quiz_par_jour,
        'ia_par_heure': ia_par_heure,
    })


@login_required
@_admin_requis
def api_gestion_utilisateurs(request):
    """Liste complète des utilisateurs pour l'admin"""
    users = User.objects.all().values(
        'id', 'username', 'first_name', 'last_name', 'email',
        'role', 'is_active', 'date_joined', 'derniere_activite', 'adresse_ip'
    )
    users_list = list(users)
    for u in users_list:
        if u['date_joined']:
            u['date_joined'] = u['date_joined'].strftime('%d/%m/%Y')
        if u['derniere_activite']:
            u['derniere_activite'] = u['derniere_activite'].strftime('%d/%m %H:%M')
    return JsonResponse({'utilisateurs': users_list})
