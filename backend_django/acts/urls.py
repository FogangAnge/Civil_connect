from django.urls import path
from rest_framework.routers import DefaultRouter

from .viewsets import BirthActViewSet, DemandeViewSet

router = DefaultRouter()
router.register(r'acts', BirthActViewSet, basename='acts')
router.register(r'demands', DemandeViewSet, basename='demands')

compat_birth_register = BirthActViewSet.as_view({'post': 'create'})
compat_verify = BirthActViewSet.as_view({'get': 'verify_qr'})
compat_demand_create = DemandeViewSet.as_view({'post': 'create'})

urlpatterns = [
    # Compat avec les routes attendues côté frontend (prompts initiaux)
    path('acts/birth-register/', compat_birth_register),
    path('acts/verify/<str:qr_hash>/', compat_verify),
    path('demands/create/', compat_demand_create),
    *router.urls,
]

