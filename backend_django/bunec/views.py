from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def stats_view(request):
    return JsonResponse(
        {
            'total_acts': 128420,
            'month_acts': 8430,
            'year_acts': 72310,
            'by_region': [
                {'region': 'Centre', 'value': 2100},
                {'region': 'Littoral', 'value': 1650},
                {'region': 'Ouest', 'value': 1420},
                {'region': 'Nord', 'value': 980},
                {'region': 'Extrême-Nord', 'value': 760},
            ],
            'monthly': [
                {'month': 'Mai', 'value': 5200},
                {'month': 'Juin', 'value': 5400},
                {'month': 'Juil', 'value': 5800},
                {'month': 'Août', 'value': 6100},
                {'month': 'Sep', 'value': 6400},
                {'month': 'Oct', 'value': 7000},
                {'month': 'Nov', 'value': 7200},
                {'month': 'Déc', 'value': 6900},
                {'month': 'Jan', 'value': 7100},
                {'month': 'Fév', 'value': 7300},
                {'month': 'Mar', 'value': 7800},
                {'month': 'Avr', 'value': 8200},
            ],
            'by_type': [
                {'name': 'Naissance', 'value': 62},
                {'name': 'Mariage', 'value': 18},
                {'name': 'Décès', 'value': 20},
            ],
        }
    )
