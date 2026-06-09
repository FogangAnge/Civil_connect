from django.urls import path

from .views import mairies_list, status_view

urlpatterns = [
    path('mairies/', mairies_list),
    path('mairies/status/', status_view),
]

