from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Epreuve, Telechargement
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_api(request):
    epreuves = Epreuve.objects.filter(est_valide=True).values(
        'id', 'titre', 'matiere__nom', 'niveau__nom', 'type_examen', 'annee', 'nb_telechargements', 'date_upload'
    )
    return Response(list(epreuves))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_telechargements(request):
    # Téléchargements des dernières 24h
    hier = timezone.now() - timezone.timedelta(hours=24)
    recent = Telechargement.objects.filter(date_telechargement__gte=hier).count()
    total = Telechargement.objects.count()
    return Response({'total': total, 'derniere_24h': recent})

urlpatterns = [
    path('', liste_api),
    path('stats/', stats_telechargements),
]
