from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Quiz, SessionQuiz

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_api(request):
    quiz = Quiz.objects.filter(est_actif=True).values(
        'id', 'titre', 'matiere__nom', 'niveau__nom', 'duree_minutes'
    )
    return Response({'quiz': list(quiz), 'total': quiz.count()})

urlpatterns = [path('', liste_api)]
