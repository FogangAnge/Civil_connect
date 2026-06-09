from django.urls import path

from .views import stats_view

urlpatterns = [
    path('bunec/stats/', stats_view),
]

