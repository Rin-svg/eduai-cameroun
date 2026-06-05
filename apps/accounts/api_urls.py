from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Utilisateur

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_utilisateurs(request):
    users = Utilisateur.objects.all().values(
        'id', 'username', 'first_name', 'last_name', 'role', 'derniere_activite', 'adresse_ip'
    )
    return Response(list(users))

urlpatterns = [
    path('', liste_utilisateurs),
]
