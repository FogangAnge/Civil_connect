from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_nin_view(request):
    nin = (request.query_params.get('nin') or '').strip()
    if len(nin) < 6:
        return JsonResponse({'valid': False, 'message': 'NIN trop court.'})
    # Mock: tout NIN numérique >= 6 est "valide"
    ok = nin.isdigit()
    return JsonResponse({'valid': ok, 'message': None if ok else 'NIN invalide.'})
