from django.urls import path

from .viewsets import AuthViewSet
from .views import verify_nin_view

auth_login = AuthViewSet.as_view({'post': 'login'})
auth_mfa = AuthViewSet.as_view({'post': 'mfa_verify'})
auth_refresh = AuthViewSet.as_view({'post': 'refresh'})

urlpatterns = [
    path('auth/login/', auth_login),
    path('auth/mfa-verify/', auth_mfa),
    path('auth/refresh/', auth_refresh),
    path('users/verify-nin/', verify_nin_view),
]

