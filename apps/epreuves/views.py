"""
EDUAI Cameroun — Vues Épreuves
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import os
from .models import Epreuve, Matiere, Niveau, Telechargement
from .forms import EpreuveForm, RechercheForm


def accueil(request):
    """Page d'accueil de la plateforme"""
    epreuves_recentes = Epreuve.objects.filter(est_valide=True).select_related('matiere', 'niveau')[:6]
    matieres = Matiere.objects.all()
    
    # Statistiques générales
    from apps.quiz.models import SessionQuiz
    from apps.accounts.models import Utilisateur
    stats = {
        'nb_epreuves': Epreuve.objects.filter(est_valide=True).count(),
        'nb_utilisateurs': Utilisateur.objects.count(),
        'nb_quiz': SessionQuiz.objects.filter(statut='termine').count(),
        'nb_matieres': Matiere.objects.count(),
    }
    return render(request, 'accueil.html', {
        'epreuves_recentes': epreuves_recentes,
        'matieres': matieres,
        'stats': stats,
    })


def liste_epreuves(request):
    form = RechercheForm(request.GET or None)
    epreuves = Epreuve.objects.filter(est_valide=True).select_related('matiere', 'niveau', 'uploade_par')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        matiere = form.cleaned_data.get('matiere')
        niveau = form.cleaned_data.get('niveau')
        type_examen = form.cleaned_data.get('type_examen')
        annee = form.cleaned_data.get('annee')

        if q:
            epreuves = epreuves.filter(
                Q(titre__icontains=q) | Q(description__icontains=q)
            )
        if matiere:
            epreuves = epreuves.filter(matiere=matiere)
        if niveau:
            epreuves = epreuves.filter(niveau=niveau)
        if type_examen:
            epreuves = epreuves.filter(type_examen=type_examen)
        if annee:
            epreuves = epreuves.filter(annee=annee)

    return render(request, 'epreuves/liste.html', {
        'epreuves': epreuves,
        'form': form,
        'total': epreuves.count(),
    })


def detail_epreuve(request, pk):
    epreuve = get_object_or_404(Epreuve, pk=pk, est_valide=True)
    epreuves_similaires = Epreuve.objects.filter(
        matiere=epreuve.matiere, est_valide=True
    ).exclude(pk=pk)[:4]
    return render(request, 'epreuves/detail.html', {
        'epreuve': epreuve,
        'similaires': epreuves_similaires,
    })


@login_required
def telecharger_epreuve(request, pk):
    epreuve = get_object_or_404(Epreuve, pk=pk, est_valide=True)

    # Vérifier activité suspecte (>50 téléchargements en 2 min)
    seuil = getattr(settings, 'SUSPICIOUS_DOWNLOAD_THRESHOLD', 50)
    limite = timezone.now() - timezone.timedelta(minutes=2)
    ip = _get_ip(request)
    nb_recent = Telechargement.objects.filter(adresse_ip=ip, date_telechargement__gte=limite).count()

    if nb_recent >= seuil:
        _creer_alerte_telechargement(ip, request.user, nb_recent)
        messages.error(request, "Activité suspecte détectée. Votre accès est temporairement limité.")
        return redirect('liste_epreuves')

    # Enregistrer le téléchargement
    Telechargement.objects.create(epreuve=epreuve, utilisateur=request.user, adresse_ip=ip)
    epreuve.nb_telechargements += 1
    epreuve.save(update_fields=['nb_telechargements'])

    if not epreuve.fichier or not os.path.exists(epreuve.fichier.path):
        raise Http404("Fichier introuvable.")

    return FileResponse(open(epreuve.fichier.path, 'rb'), as_attachment=True,
                        filename=os.path.basename(epreuve.fichier.name))


@login_required
def upload_epreuve(request):
    if not (request.user.est_enseignant or request.user.est_admin):
        messages.error(request, "Seuls les enseignants peuvent uploader des épreuves.")
        return redirect('liste_epreuves')

    if request.method == 'POST':
        form = EpreuveForm(request.POST, request.FILES)
        if form.is_valid():
            epreuve = form.save(commit=False)
            epreuve.uploade_par = request.user
            epreuve.save()
            messages.success(request, f"Épreuve « {epreuve.titre} » uploadée avec succès !")
            return redirect('detail_epreuve', pk=epreuve.pk)
    else:
        form = EpreuveForm()

    return render(request, 'epreuves/upload.html', {'form': form})


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def _creer_alerte_telechargement(ip, user, nb):
    try:
        from apps.securite.models import AlerteSecurite
        AlerteSecurite.objects.create(
            niveau='avertissement',
            titre=f"Téléchargements massifs — IP {ip}",
            message=f"L'utilisateur {user} (IP: {ip}) a effectué {nb} téléchargements en moins de 2 minutes.",
            adresse_ip=ip,
        )
    except Exception:
        pass
