from django.urls import path
from rest_framework.routers import DefaultRouter

from .viewsets import DeclarationHopitaliereViewSet

router = DefaultRouter()
router.register(r'hospital-declarations', DeclarationHopitaliereViewSet, basename='hospital-declarations')

urlpatterns = [
    *router.urls,
]

