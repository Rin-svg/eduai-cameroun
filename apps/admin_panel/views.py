"""
EDUAI Cameroun — Tableau de bord Administrateur
URL : /admin-panel/
Accès réservé aux utilisateurs avec role='admin' ou is_superuser=True
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
import json
from datetime import timedelta

from apps.accounts.models import Utilisateur
from apps.quiz.models import SessionQuiz, Quiz
from apps.epreuves.models import Epreuve, Telechargement
from apps.securite.models import TentativeConnexion


def admin_requis(view_func):
    """Décorateur : réserve la vue aux admins."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.role == 'admin' or request.user.is_superuser):
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('accueil')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_requis
def dashboard(request):
    """Page principale du tableau de bord admin."""
    now = timezone.now()
    aujourd_hui = now.date()
    il_y_a_7j  = now - timedelta(days=7)
    il_y_a_30j = now - timedelta(days=30)

    # ── Compteurs principaux ──────────────────────────────────────────────────
    total_eleves      = Utilisateur.objects.filter(role='eleve').count()
    total_enseignants = Utilisateur.objects.filter(role='enseignant').count()
    total_epreuves    = Epreuve.objects.filter(est_valide=True).count()
    total_quiz        = Quiz.objects.filter(est_actif=True).count()

    # Actifs aujourd'hui (dernière activité aujourd'hui)
    actifs_auj = Utilisateur.objects.filter(
        derniere_activite__date=aujourd_hui
    ).count()

    # Sessions quiz aujourd'hui
    quiz_auj = SessionQuiz.objects.filter(
        date_debut__date=aujourd_hui
    ).count()

    # Téléchargements aujourd'hui
    dl_auj = Telechargement.objects.filter(
        date_telechargement__date=aujourd_hui
    ).count()

    # Alertes brute force actives
    alertes_bf = TentativeConnexion.objects.filter(
        est_bloque=True,
        fin_blocage__gt=now
    ).count()

    # ── Graphique activité 7 derniers jours ───────────────────────────────────
    labels_7j, sessions_7j, dl_7j = [], [], []
    for i in range(6, -1, -1):
        jour = aujourd_hui - timedelta(days=i)
        labels_7j.append(jour.strftime('%d/%m'))
        sessions_7j.append(
            SessionQuiz.objects.filter(date_debut__date=jour).count()
        )
        dl_7j.append(
            Telechargement.objects.filter(date_telechargement__date=jour).count()
        )

    # ── Score moyen global ────────────────────────────────────────────────────
    score_moyen = SessionQuiz.objects.filter(
        statut='termine'
    ).aggregate(m=Avg('score_obtenu'))['m'] or 0

    # ── Dernières inscriptions ────────────────────────────────────────────────
    derniers_inscrits = Utilisateur.objects.exclude(
        role='admin'
    ).order_by('-date_inscription')[:8]

    # ── Dernières sessions quiz ───────────────────────────────────────────────
    dernieres_sessions = SessionQuiz.objects.select_related(
        'utilisateur', 'quiz'
    ).order_by('-date_debut')[:8]

    # ── Épreuves en attente de validation ────────────────────────────────────
    epreuves_non_validees = Epreuve.objects.filter(
        est_valide=False
    ).select_related('matiere', 'niveau', 'uploade_par')[:5]

    # ── Top épreuves téléchargées ─────────────────────────────────────────────
    top_epreuves = Epreuve.objects.order_by('-nb_telechargements')[:5]

    context = {
        # Compteurs
        'total_eleves':      total_eleves,
        'total_enseignants': total_enseignants,
        'total_epreuves':    total_epreuves,
        'total_quiz':        total_quiz,
        'actifs_auj':        actifs_auj,
        'quiz_auj':          quiz_auj,
        'dl_auj':            dl_auj,
        'alertes_bf':        alertes_bf,
        'score_moyen':       round(score_moyen, 1),
        # Graphique
        'labels_7j':    json.dumps(labels_7j),
        'sessions_7j':  json.dumps(sessions_7j),
        'dl_7j':        json.dumps(dl_7j),
        # Listes
        'derniers_inscrits':    derniers_inscrits,
        'dernieres_sessions':   dernieres_sessions,
        'epreuves_non_validees': epreuves_non_validees,
        'top_epreuves':         top_epreuves,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_requis
def liste_utilisateurs(request):
    """Liste et recherche des utilisateurs."""
    q    = request.GET.get('q', '')
    role = request.GET.get('role', '')

    users = Utilisateur.objects.all()
    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )
    if role:
        users = users.filter(role=role)

    users = users.order_by('-date_inscription')

    return render(request, 'admin_panel/utilisateurs.html', {
        'users': users,
        'q': q,
        'role_filtre': role,
    })


@admin_requis
@require_POST
def toggle_actif(request, user_id):
    """Activer / Suspendre un compte utilisateur."""
    user = get_object_or_404(Utilisateur, id=user_id)
    if user == request.user:
        return JsonResponse({'erreur': 'Vous ne pouvez pas vous suspendre vous-même.'}, status=400)
    user.is_active = not user.is_active
    user.save()
    statut = 'activé' if user.is_active else 'suspendu'
    return JsonResponse({
        'is_active': user.is_active,
        'message': f"Compte {user.username} {statut}."
    })


@admin_requis
@require_POST
def reset_password(request, user_id):
    """Réinitialise le mot de passe à EduAI2025!"""
    user = get_object_or_404(Utilisateur, id=user_id)
    nouveau_mdp = 'EduAI2025!'
    user.set_password(nouveau_mdp)
    user.save()
    return JsonResponse({
        'message': f"Mot de passe de {user.username} réinitialisé à : {nouveau_mdp}"
    })


@admin_requis
@require_POST
def creer_utilisateur(request):
    """Créer un compte élève ou enseignant rapidement."""
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        prenom   = data.get('prenom', '').strip()
        nom      = data.get('nom', '').strip()
        email    = data.get('email', '').strip()
        role     = data.get('role', 'eleve')
        classe   = data.get('classe', '').strip()

        if not username:
            return JsonResponse({'erreur': 'Nom d\'utilisateur requis.'}, status=400)
        if Utilisateur.objects.filter(username=username).exists():
            return JsonResponse({'erreur': 'Ce nom d\'utilisateur existe déjà.'}, status=400)

        user = Utilisateur.objects.create_user(
            username=username,
            password='EduAI2025!',
            first_name=prenom,
            last_name=nom,
            email=email,
            role=role,
            classe=classe,
        )
        return JsonResponse({
            'message': f"Compte {username} créé. Mot de passe par défaut : EduAI2025!",
            'user_id': user.id,
        })
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=500)


@admin_requis
def valider_epreuve(request, epreuve_id):
    """Valider une épreuve uploadée par un enseignant."""
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)
    epreuve.est_valide = True
    epreuve.save()
    messages.success(request, f"Épreuve « {epreuve.titre} » validée.")
    return redirect('admin_panel:dashboard')


@admin_requis
def stats_json(request):
    """API JSON pour les stats en temps réel (rafraîchissement auto)."""
    now = timezone.now()
    return JsonResponse({
        'actifs_auj':  Utilisateur.objects.filter(derniere_activite__date=now.date()).count(),
        'quiz_auj':    SessionQuiz.objects.filter(date_debut__date=now.date()).count(),
        'alertes_bf':  TentativeConnexion.objects.filter(est_bloque=True, fin_blocage__gt=now).count(),
    })
