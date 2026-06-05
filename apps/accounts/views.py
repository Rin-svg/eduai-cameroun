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
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès ! Bienvenue sur EDUAI Cameroun.")
            return redirect('accueil')
    else:
        form = InscriptionForm()

    return render(request, 'accounts/inscription.html', {'form': form})


@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('connexion')


@login_required
def profil(request):
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profil')
    else:
        form = ProfilForm(instance=request.user)

    # Stats de l'utilisateur
    from apps.quiz.models import SessionQuiz
    from apps.epreuves.models import Telechargement
    sessions = SessionQuiz.objects.filter(utilisateur=request.user, statut='termine')
    telechargements = Telechargement.objects.filter(utilisateur=request.user).count()

    context = {
        'form': form,
        'nb_quiz': sessions.count(),
        'score_moyen': sessions.aggregate(
            moy=__import__('django.db.models', fromlist=['Avg']).Avg('score_obtenu')
        )['moy'] or 0,
        'nb_telechargements': telechargements,
    }
    return render(request, 'accounts/profil.html', context)


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
