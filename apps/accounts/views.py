"""
EDUAI Cameroun — Vues Comptes Utilisateurs
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import Utilisateur
from .forms import ConnexionForm, InscriptionForm, ProfilForm
from .forms import InscriptionEleveForm, InscriptionEnseignantForm



def connexion(request):
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                # Réinitialiser les tentatives
                _reinitialiser_tentatives(request)
                login(request, user)
                user.adresse_ip = _get_ip(request)
                user.save(update_fields=['adresse_ip', 'derniere_activite'])
                messages.success(request, f"Bienvenue, {user.get_full_name() or user.username} !")
                return redirect(request.GET.get('next', 'accueil'))
            else:
                _enregistrer_tentative(request, username)
                messages.error(request, "Identifiants incorrects. Vérifiez votre nom d'utilisateur et mot de passe.")
    else:
        form = ConnexionForm()

    return render(request, 'accounts/connexion.html', {'form': form})


def inscription(request):
    """Page de choix du type de compte."""
    if request.user.is_authenticated:
        return redirect('accueil')
    return render(request, 'accounts/inscription_choix.html')


def inscription_eleve(request):
    """Inscription élève."""
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        form = InscriptionEleveForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name} ! Ton compte élève est créé.")
            return redirect('accueil')
    else:
        form = InscriptionEleveForm()

    return render(request, 'accounts/inscription_eleve.html', {'form': form})


def inscription_enseignant(request):
    """Inscription enseignant — protégée par code."""
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        form = InscriptionEnseignantForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte enseignant est actif.")
            return redirect('accueil')
    else:
        form = InscriptionEnseignantForm()

    return render(request, 'accounts/inscription_enseignant.html', {'form': form})


@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('connexion')


@login_required
def profil(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'modifier_profil')

        # ── Action 1 : modifier le profil ─────────────────────────────────────
        if action == 'modifier_profil':
            form = ProfilForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profil mis à jour avec succès.")
                return redirect('profil')
            else:
                messages.error(request, "Veuillez corriger les erreurs ci-dessous.")

        # ── Action 2 : changer le mot de passe ────────────────────────────────
        elif action == 'changer_mdp':
            form = ProfilForm(instance=request.user)
            ancien_mdp   = request.POST.get('ancien_mdp', '')
            nouveau_mdp  = request.POST.get('nouveau_mdp', '')
            confirmer    = request.POST.get('confirmer_mdp', '')

            if not request.user.check_password(ancien_mdp):
                messages.error(request, "Mot de passe actuel incorrect.")
            elif nouveau_mdp != confirmer:
                messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
            elif len(nouveau_mdp) < 8:
                messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            else:
                request.user.set_password(nouveau_mdp)
                request.user.save()
                # Maintenir la session active après changement de mdp
                update_session_auth_hash(request, request.user)
                messages.success(request, "Mot de passe modifié avec succès !")
                return redirect('profil')
    else:
        form = ProfilForm(instance=request.user)

    # Stats
    from apps.quiz.models import SessionQuiz
    from apps.epreuves.models import Telechargement
    from django.db.models import Avg

    sessions        = SessionQuiz.objects.filter(utilisateur=request.user, statut='termine')
    nb_telechargements = Telechargement.objects.filter(utilisateur=request.user).count()

    return render(request, 'accounts/profil.html', {
        'form':               form,
        'nb_quiz':            sessions.count(),
        'score_moyen':        sessions.aggregate(moy=Avg('score_obtenu'))['moy'] or 0,
        'nb_telechargements': nb_telechargements,
    })



def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def _enregistrer_tentative(request, username):
    try:
        from apps.securite.models import TentativeConnexion, AlerteSecurite
        ip = _get_ip(request)
        tentative, created = TentativeConnexion.objects.get_or_create(adresse_ip=ip)
        tentative.username = username
        tentative.nb_tentatives += 1
        tentative.save()

        max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
        if tentative.nb_tentatives >= max_attempts:
            lockout_min = getattr(settings, 'LOCKOUT_DURATION_MINUTES', 15)
            tentative.est_bloque = True
            tentative.fin_blocage = timezone.now() + timezone.timedelta(minutes=lockout_min)
            tentative.save()
            AlerteSecurite.objects.create(
                niveau='critique',
                titre=f"Brute Force détecté — IP {ip}",
                message=f"L'IP {ip} a effectué {tentative.nb_tentatives} tentatives de connexion (user: {username}). IP bloquée pour {lockout_min} minutes.",
                adresse_ip=ip,
            )
    except Exception:
        pass


def _reinitialiser_tentatives(request):
    try:
        from apps.securite.models import TentativeConnexion
        ip = _get_ip(request)
        TentativeConnexion.objects.filter(adresse_ip=ip).update(
            nb_tentatives=0, est_bloque=False, fin_blocage=None
        )
    except Exception:
        pass
