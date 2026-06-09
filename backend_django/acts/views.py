from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['POST'])
@permission_classes([AllowAny])
def birth_register_view(request):
    # À implémenter: validation, signature, génération QR, persistance, audit
    return JsonResponse({'status': 'ok', 'message': 'Acte de naissance enregistré (mock).'})


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_act_view(request, qr_hash: str):
    # Mock: hash commençant par "OK" est valide
    valid = qr_hash.upper().startswith('OK')
    if not valid:
        return JsonResponse({'valid': False, 'message': 'Acte invalide.'})
    return JsonResponse(
        {
            'valid': True,
            'nom': 'DOE',
            'date': '2026-01-12',
            'mairie': 'Yaoundé I',
            'officier': 'Officier Demo',
            'statut': 'VALIDE',
        }
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def demand_create_view(request):
    # À implémenter: workflow demande, paiement, livraison, notifications
    return JsonResponse({'status': 'ok', 'id': 1024})
