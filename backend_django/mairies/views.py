from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Mairie


@api_view(['GET'])
@permission_classes([AllowAny])
def mairies_list(request):
    return JsonResponse(
        list(
            Mairie.objects.order_by('code').values('code', 'nom', 'region', 'departement', 'commune')
        ),
        safe=False,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def status_view(request):
    return JsonResponse(
        [
            {
                'name': 'Mairie Yaoundé I',
                'region': 'Centre',
                'month_acts': 320,
                'total_acts': 12450,
                'status': 'ONLINE',
                'last_sync': 'il y a 5 min',
            },
            {
                'name': 'Mairie Douala II',
                'region': 'Littoral',
                'month_acts': 280,
                'total_acts': 10210,
                'status': 'ONLINE',
                'last_sync': 'il y a 12 min',
            },
            {
                'name': 'Mairie Bafoussam',
                'region': 'Ouest',
                'month_acts': 140,
                'total_acts': 7420,
                'status': 'OFFLINE',
                'last_sync': 'il y a 28h',
            },
        ],
        safe=False,
    )
