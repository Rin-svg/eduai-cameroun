"""
EDUAI Cameroun — Module Intelligence Artificielle
Correction automatique, chatbot pédagogique, analyse de plagiat
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os

try:
    from openai import OpenAI
    OPENAI_DISPONIBLE = True
except ImportError:
    OPENAI_DISPONIBLE = False


def _get_client():
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key or not OPENAI_DISPONIBLE:
        return None
    return OpenAI(api_key=api_key)


@login_required
def accueil_ia(request):
    return render(request, 'ia/accueil.html', {
        'openai_disponible': bool(getattr(settings, 'OPENAI_API_KEY', '')),
    })


@login_required
@require_POST
def corriger_reponse(request):
    """Correction automatique d'une réponse ouverte via OpenAI."""
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        reponse_eleve = data.get('reponse', '').strip()
        matiere = data.get('matiere', 'général')

        if not question or not reponse_eleve:
            return JsonResponse({'erreur': 'Question et réponse requises.'}, status=400)

        client = _get_client()
        if not client:
            # Mode démo sans clé API
            return JsonResponse({
                'score': 14,
                'note_sur_20': 14,
                'appreciation': 'Bien',
                'commentaire': '[Mode démo — API OpenAI non configurée] La réponse démontre une bonne compréhension du sujet. Les points principaux sont correctement identifiés.',
                'points_forts': ['Bonne structure', 'Vocabulaire adapté'],
                'points_amelioration': ['Développer les exemples', 'Approfondir la conclusion'],
                'mode_demo': True,
            })

        prompt = f"""Tu es un correcteur pédagogique camerounais expert en {matiere}.
        
Question : {question}
Réponse de l'élève : {reponse_eleve}

Corrige cette réponse et fournis une évaluation structurée en JSON avec les champs :
- score (sur 20)
- appreciation (Excellent/Très bien/Bien/Passable/Insuffisant)
- commentaire (feedback général, 2-3 phrases)
- points_forts (liste des éléments corrects)
- points_amelioration (liste des éléments à améliorer)
- suggestions_revision (ressources ou thèmes à revoir)

Réponds UNIQUEMENT en JSON valide."""

        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": "Tu es un correcteur pédagogique expert. Tu réponds uniquement en JSON valide."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3,
        )

        texte = response.choices[0].message.content.strip()
        # Nettoyer les balises markdown si présentes
        if texte.startswith('```'):
            texte = texte.split('```')[1]
            if texte.startswith('json'):
                texte = texte[4:]

        resultat = json.loads(texte)
        resultat['note_sur_20'] = resultat.get('score', 0)
        resultat['mode_demo'] = False

        # Journaliser
        _journaliser_ia(request, 'correction', len(reponse_eleve))
        return JsonResponse(resultat)

    except json.JSONDecodeError:
        return JsonResponse({'erreur': 'Réponse IA invalide. Réessayez.'}, status=500)
    except Exception as e:
        return JsonResponse({'erreur': f'Erreur IA : {str(e)}'}, status=500)


@login_required
@require_POST
def chatbot(request):
    """Chatbot pédagogique pour les questions des élèves."""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        historique = data.get('historique', [])

        if not message:
            return JsonResponse({'erreur': 'Message vide.'}, status=400)

        client = _get_client()
        if not client:
            reponses_demo = [
                "Je suis EduBot, votre assistant pédagogique EDUAI Cameroun ! En mode démo, je ne peux pas répondre aux questions spécifiques, mais une fois l'API OpenAI configurée, je pourrai vous aider sur toutes les matières.",
                "Pour configurer l'IA, demandez à votre administrateur de renseigner la clé API OpenAI dans le fichier .env du serveur.",
                "Les fonctionnalités disponibles en mode démo : correction automatique simulée, quiz interactifs, bibliothèque d'épreuves.",
            ]
            import random
            return JsonResponse({'reponse': random.choice(reponses_demo), 'mode_demo': True})

        messages_api = [
            {"role": "system", "content": (
                "Tu es EduBot, l'assistant pédagogique de la plateforme EDUAI Cameroun. "
                "Tu aides les élèves et enseignants camerounais dans leurs études. "
                "Tu réponds en français, de façon claire et pédagogique, adaptée au niveau scolaire camerounais. "
                "Tu connais les programmes du MINESEC (Ministère des Enseignements Secondaires du Cameroun). "
                "Si on te pose des questions hors sujet éducatif, redirige gentiment vers les études."
            )}
        ]

        # Ajouter l'historique
        for msg in historique[-6:]:  # Garder les 6 derniers messages
            messages_api.append({"role": msg['role'], "content": msg['content']})
        messages_api.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=messages_api,
            max_tokens=600,
            temperature=0.7,
        )

        reponse = response.choices[0].message.content.strip()
        _journaliser_ia(request, 'chatbot', len(message))
        return JsonResponse({'reponse': reponse, 'mode_demo': False})

    except Exception as e:
        return JsonResponse({'erreur': f'Erreur : {str(e)}'}, status=500)


@login_required
@require_POST
def detecter_plagiat(request):
    """Détection de similarité entre deux textes."""
    try:
        data = json.loads(request.body)
        texte1 = data.get('texte1', '').strip()
        texte2 = data.get('texte2', '').strip()

        if not texte1 or not texte2:
            return JsonResponse({'erreur': 'Les deux textes sont requis.'}, status=400)

        client = _get_client()
        if not client:
            return JsonResponse({
                'similarite_pourcent': 23,
                'verdict': 'Faible similarité',
                'explication': '[Mode démo] Analyse de plagiat simulée. La similarité détectée est faible.',
                'mode_demo': True,
            })

        prompt = f"""Analyse la similarité entre ces deux textes et détecte le plagiat éventuel.

Texte 1 : {texte1[:1000]}
Texte 2 : {texte2[:1000]}

Réponds en JSON avec :
- similarite_pourcent (0-100)
- verdict (Plagiat fort/Plagiat probable/Faible similarité/Aucun plagiat)
- passages_similaires (liste des extraits suspects)
- explication (analyse détaillée)"""

        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": "Expert en détection de plagiat. Réponds uniquement en JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1,
        )

        texte = response.choices[0].message.content.strip()
        if texte.startswith('```'):
            texte = texte.split('```')[1]
            if texte.startswith('json'):
                texte = texte[4:]

        resultat = json.loads(texte)
        resultat['mode_demo'] = False
        return JsonResponse(resultat)

    except Exception as e:
        return JsonResponse({'erreur': f'Erreur : {str(e)}'}, status=500)


def _journaliser_ia(request, type_req, nb_chars):
    try:
        from apps.securite.models import LogActivite
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        LogActivite.objects.create(
            utilisateur=request.user,
            type_action='ia',
            description=f"Requête IA : {type_req} ({nb_chars} caractères)",
            adresse_ip=ip,
            details={'type': type_req, 'nb_chars': nb_chars},
        )
    except Exception:
        pass
