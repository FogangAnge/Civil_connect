from rest_framework.routers import DefaultRouter

from .viewsets import OCRViewSet

router = DefaultRouter()
router.register(r'ocr', OCRViewSet, basename='ocr')

urlpatterns = router.urls

