"""
EDUAI Cameroun — Vues Quiz Interactif
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import json
from .models import Quiz, Question, Choix, SessionQuiz, ReponseEleve


def liste_quiz(request):
    quiz_list = Quiz.objects.filter(est_actif=True).select_related('matiere', 'niveau', 'cree_par')
    return render(request, 'quiz/liste.html', {'quiz_list': quiz_list})


@login_required
def demarrer_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, est_actif=True)

    # Vérifier nb tentatives max
    nb_tentatives = SessionQuiz.objects.filter(utilisateur=request.user, quiz=quiz).count()
    if nb_tentatives >= quiz.nb_tentatives_max:
        messages.warning(request, f"Vous avez atteint le nombre maximum de tentatives ({quiz.nb_tentatives_max}) pour ce quiz.")
        return redirect('liste_quiz')

    # Créer la session
    session = SessionQuiz.objects.create(
        quiz=quiz,
        utilisateur=request.user,
        adresse_ip=_get_ip(request),
    )
    return redirect('passer_quiz', session_id=session.pk)


@login_required
def passer_quiz(request, session_id):
    session = get_object_or_404(SessionQuiz, pk=session_id, utilisateur=request.user, statut='en_cours')
    quiz = session.quiz
    questions = quiz.questions.prefetch_related('choix').all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            if question.type_question in ['qcm', 'vrai_faux']:
                choix_id = request.POST.get(f'question_{question.pk}')
                if choix_id:
                    try:
                        choix = Choix.objects.get(pk=choix_id, question=question)
                        est_correcte = choix.est_correct
                        points = question.points if est_correcte else 0
                        score += points
                        ReponseEleve.objects.create(
                            session=session,
                            question=question,
                            choix_selectionne=choix,
                            est_correcte=est_correcte,
                            points_obtenus=points,
                        )
                    except Choix.DoesNotExist:
                        pass
            else:
                texte = request.POST.get(f'question_{question.pk}', '').strip()
                ReponseEleve.objects.create(
                    session=session, question=question,
                    texte_reponse=texte, est_correcte=False, points_obtenus=0,
                )

        session.score_obtenu = score
        session.date_fin = timezone.now()
        session.statut = 'termine'
        session.save()
        return redirect('resultat_quiz', session_id=session.pk)

    return render(request, 'quiz/passer.html', {
        'session': session, 'quiz': quiz, 'questions': questions,
    })


@login_required
def resultat_quiz(request, session_id):
    session = get_object_or_404(SessionQuiz, pk=session_id, utilisateur=request.user)
    reponses = session.reponses.select_related('question', 'choix_selectionne').all()
    
    # Classement
    classement = SessionQuiz.objects.filter(quiz=session.quiz, statut='termine').order_by('-score_obtenu')[:10]
    
    return render(request, 'quiz/resultat.html', {
        'session': session, 'reponses': reponses, 'classement': classement,
    })


@login_required
def mes_resultats(request):
    sessions = SessionQuiz.objects.filter(
        utilisateur=request.user, statut='termine'
    ).select_related('quiz', 'quiz__matiere').order_by('-date_fin')
    return render(request, 'quiz/mes_resultats.html', {'sessions': sessions})


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')
