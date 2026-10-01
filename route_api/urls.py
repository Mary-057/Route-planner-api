from django.urls import path
from . import views

urlpatterns = [
    path('plan-route/', views.get_route, name='plan-route'),
]