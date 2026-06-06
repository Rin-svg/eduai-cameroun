"""
EDUAI Cameroun — Module Intelligence Artificielle
Correction automatique, chatbot pédagogique, analyse de plagiat
Powered by Google Gemini (gemini-2.0-flash)
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import json
import urllib.request
import urllib.error


GEMINI_MODEL = "gemini-3.5-flash"
GEMINI_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)


def _get_api_key():
    return getattr(settings, 'GEMINI_API_KEY', '')


def _appel_gemini(messages, max_tokens=8192, temperature=0.7):
    """Appel à l'API Google Gemini avec le format /v1beta/models/...:generateContent"""
    api_key = _get_api_key()
    if not api_key:
        return None

    # Convertir le format OpenAI (role/content) vers Gemini (parts)
    contents = []
    system_instruction = None

    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        if role == 'system':
            system_instruction = content
        else:
            gemini_role = 'user' if role == 'user' else 'model'
            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })

    payload = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        }
    }
    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    url = GEMINI_URL_TEMPLATE.format(model=GEMINI_MODEL, key=api_key)
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
        return resp['candidates'][0]['content']['parts'][0]['text'].strip()


def _nettoyer_json(texte):
    texte = texte.strip()
    if texte.startswith('```'):
        lignes = texte.split('\n')
        texte = '\n'.join(lignes[1:-1])
        if texte.startswith('json'):
            texte = texte[4:]
    return texte.strip()


@login_required
def accueil_ia(request):
    return render(request, 'ia/accueil.html', {
        'openai_disponible': bool(_get_api_key()),
    })


@login_required
@require_POST
def corriger_reponse(request):
    try:
        data = json.loads(request.body)
        question      = data.get('question', '').strip()
        reponse_eleve = data.get('reponse', '').strip()
        matiere       = data.get('matiere', 'general')

        if not question or not reponse_eleve:
            return JsonResponse({'erreur': 'Question et reponse requises.'}, status=400)

        if not _get_api_key():
            return JsonResponse({
                'score': 14, 'note_sur_20': 14,
                'appreciation': 'Bien',
                'commentaire': '[Mode demo] La reponse demontre une bonne comprehension du sujet.',
                'points_forts': ['Bonne structure', 'Vocabulaire adapte'],
                'points_amelioration': ['Developper les exemples', 'Approfondir la conclusion'],
                'mode_demo': True,
            })

        messages = [
            {
                "role": "system",
                "content": (
                    f"Tu es un correcteur pedagogique camerounais expert en {matiere}, "
                    "selon les standards du MINESEC. "
                    "Tu reponds UNIQUEMENT en JSON valide, sans balises markdown."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Question : {question}\n"
                    f"Reponse de l'eleve : {reponse_eleve}\n\n"
                    "Evalue cette reponse. Reponds en JSON avec exactement ces champs :\n"
                    '{"score": <0-20>, "appreciation": "<Excellent|Tres bien|Bien|Passable|Insuffisant>", '
                    '"commentaire": "<2-3 phrases>", "points_forts": ["..."], '
                    '"points_amelioration": ["..."], "suggestions_revision": ["..."]}'
                )
            }
        ]

        texte = _appel_gemini(messages, max_tokens=8192, temperature=0.3)
        resultat = json.loads(_nettoyer_json(texte))
        resultat['note_sur_20'] = resultat.get('score', 0)
        resultat['mode_demo'] = False
        _journaliser_ia(request, 'correction', len(reponse_eleve))
        return JsonResponse(resultat)

    except json.JSONDecodeError:
        return JsonResponse({'erreur': 'Reponse IA invalide. Reessayez.'}, status=500)
    except Exception as e:
        return JsonResponse({'erreur': f'Erreur IA : {str(e)}'}, status=500)


@login_required
@require_POST
def chatbot(request):
    try:
        data       = json.loads(request.body)
        message    = data.get('message', '').strip()
        historique = data.get('historique', [])

        if not message:
            return JsonResponse({'erreur': 'Message vide.'}, status=400)

        if not _get_api_key():
            import random
            return JsonResponse({
                'reponse': random.choice([
                    "Je suis EduBot ! En mode demo, configurez la cle API Gemini pour des reponses reelles.",
                    "Demandez a l'administrateur de configurer GEMINI_API_KEY dans le fichier .env.",
                ]),
                'mode_demo': True
            })

        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es EduBot, l'assistant pedagogique de la plateforme EDUAI Cameroun. "
                    "Tu aides les eleves et enseignants camerounais. "
                    "Tu reponds en francais, de facon claire et adaptee au niveau scolaire camerounais. "
                    "Tu connais les programmes du MINESEC. "
                    "Si la question est hors sujet educatif, redirige gentiment vers les etudes."
                )
            }
        ]

        for msg in historique[-6:]:
            messages.append({"role": msg['role'], "content": msg['content']})
        messages.append({"role": "user", "content": message})

        texte = _appel_gemini(messages, max_tokens=8192, temperature=0.7)
        _journaliser_ia(request, 'chatbot', len(message))
        return JsonResponse({'reponse': texte, 'mode_demo': False})

    except Exception as e:
        return JsonResponse({'erreur': f'Erreur : {str(e)}'}, status=500)


@login_required
@require_POST
def detecter_plagiat(request):
    try:
        data   = json.loads(request.body)
        texte1 = data.get('texte1', '').strip()
        texte2 = data.get('texte2', '').strip()

        if not texte1 or not texte2:
            return JsonResponse({'erreur': 'Les deux textes sont requis.'}, status=400)

        if not _get_api_key():
            return JsonResponse({
                'similarite_pourcent': 23,
                'verdict': 'Faible similarite',
                'explication': '[Mode demo] Analyse simulee.',
                'passages_similaires': [],
                'mode_demo': True,
            })

        messages = [
            {
                "role": "system",
                "content": "Tu es un expert en detection de plagiat. Tu reponds UNIQUEMENT en JSON valide, sans balises markdown."
            },
            {
                "role": "user",
                "content": (
                    f"Texte 1 : {texte1[:1200]}\n\n"
                    f"Texte 2 : {texte2[:1200]}\n\n"
                    "Analyse la similarite. Reponds en JSON :\n"
                    '{"similarite_pourcent": <0-100>, '
                    '"verdict": "<Plagiat fort|Plagiat probable|Faible similarite|Aucun plagiat>", '
                    '"passages_similaires": ["..."], '
                    '"explication": "<2-3 phrases>"}'
                )
            }
        ]

        texte = _appel_gemini(messages, max_tokens=8192, temperature=0.1)
        resultat = json.loads(_nettoyer_json(texte))
        resultat['mode_demo'] = False
        return JsonResponse(resultat)

    except json.JSONDecodeError:
        return JsonResponse({'erreur': 'Reponse IA invalide. Reessayez.'}, status=500)
    except Exception as e:
        return JsonResponse({'erreur': f'Erreur : {str(e)}'}, status=500)


def _journaliser_ia(request, type_req, nb_chars):
    try:
        from apps.securite.models import LogActivite
        LogActivite.objects.create(
            utilisateur=request.user,
            type_action='ia',
            description=f"Requete IA : {type_req} ({nb_chars} caracteres)",
            adresse_ip=request.META.get('REMOTE_ADDR', '0.0.0.0'),
            details={'type': type_req, 'nb_chars': nb_chars},
        )
    except Exception:
        pass


@login_required
@require_POST
def generer_quiz(request):
    """
    Génère un quiz complet via Gemini et l'enregistre en base de données.
    Payload JSON : { matiere, niveau, nb_questions, difficulte, sujet }
    """
    try:
        data         = json.loads(request.body)
        matiere_nom  = data.get('matiere', '').strip()
        niveau_nom   = data.get('niveau', '').strip()
        nb_questions = max(2, min(int(data.get('nb_questions', 5)), 10))
        difficulte   = data.get('difficulte', 'moyen')
        sujet        = data.get('sujet', '').strip()

        if not matiere_nom or not niveau_nom:
            return JsonResponse({'erreur': 'Matiere et niveau requis.'}, status=400)

        # ── Mode démo (sans clé API) ──────────────────────────────────────
        if not _get_api_key():
            return JsonResponse({
                'mode_demo': True,
                'message': 'Configurez GEMINI_API_KEY dans .env pour générer de vrais quiz.',
                'apercu': {
                    'titre': f'Quiz {matiere_nom} — {niveau_nom} [DEMO]',
                    'questions': [
                        {'enonce': 'Question exemple (mode démo)', 'choix': ['A) Réponse 1', 'B) Réponse 2'], 'correct': 'A'},
                    ]
                }
            })

        # ── Prompt Gemini ─────────────────────────────────────────────────
        sujet_info = f" sur le sujet : {sujet}" if sujet else ""
        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un professeur expert camerounais qui crée des quiz pédagogiques "
                    "selon les programmes du MINESEC. "
                    "Tu réponds UNIQUEMENT en JSON valide, sans balises markdown ni texte autour."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Crée un quiz de {nb_questions} questions en {matiere_nom} "
                    f"pour le niveau {niveau_nom}{sujet_info}. "
                    f"Difficulté : {difficulte}. "
                    f"Réponds UNIQUEMENT avec ce JSON (rien d'autre) :\n"
                    '{"titre": "...", "description": "...", '
                    '"questions": ['
                    '{"enonce": "...", "type": "qcm", "points": 1, '
                    '"choix": [{"texte": "...", "correct": true/false}, ...], '
                    '"explication": "..."}'
                    ']}'
                )
            }
        ]

        texte   = _appel_gemini(messages, max_tokens=4096, temperature=0.6)
        payload = json.loads(_nettoyer_json(texte))

        # ── Enregistrement en base ────────────────────────────────────────
        from apps.epreuves.models import Matiere, Niveau
        from apps.quiz.models import Quiz, Question, Choix as QuizChoix

        matiere_obj = Matiere.objects.filter(nom__icontains=matiere_nom).first()
        niveau_obj  = Niveau.objects.filter(nom__icontains=niveau_nom).first()

        if not matiere_obj or not niveau_obj:
            return JsonResponse({
                'erreur': f'Matière "{matiere_nom}" ou niveau "{niveau_nom}" introuvable en base.',
                'apercu': payload,
            }, status=400)

        duree = nb_questions * 3  # 3 min par question

        quiz = Quiz.objects.create(
            titre       = payload.get('titre', f'Quiz {matiere_nom} — {niveau_nom}'),
            description = payload.get('description', ''),
            matiere     = matiere_obj,
            niveau      = niveau_obj,
            duree_minutes = duree,
            cree_par    = request.user,
            est_actif   = True,
        )

        for i, q_data in enumerate(payload.get('questions', []), 1):
            question = Question.objects.create(
                quiz          = quiz,
                enonce        = q_data.get('enonce', ''),
                type_question = q_data.get('type', 'qcm'),
                points        = int(q_data.get('points', 1)),
                ordre         = i,
                explication   = q_data.get('explication', ''),
            )
            for j, c in enumerate(q_data.get('choix', []), 1):
                QuizChoix.objects.create(
                    question   = question,
                    texte      = c.get('texte', ''),
                    est_correct= bool(c.get('correct', False)),
                    ordre      = j,
                )

        _journaliser_ia(request, 'generation_quiz', nb_questions)

        return JsonResponse({
            'mode_demo': False,
            'succes'   : True,
            'quiz_id'  : quiz.pk,
            'quiz_titre': quiz.titre,
            'nb_questions': quiz.nb_questions,
            'url_quiz' : f'/quiz/{quiz.pk}/demarrer/',
            'message'  : f'Quiz "{quiz.titre}" créé avec {quiz.nb_questions} questions !',
        })

    except json.JSONDecodeError:
        return JsonResponse({'erreur': 'Réponse IA invalide. Réessayez.'}, status=500)
    except Exception as e:
        return JsonResponse({'erreur': f'Erreur : {str(e)}'}, status=500)
