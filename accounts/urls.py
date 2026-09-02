from django.urls import path
from . import views

urlpatterns = [
    path('register-device/', views.register_device, name='register-device'),
    path('me/', views.me, name='me'),
    path('me/update/', views.update_profile, name='update-profile'),
]