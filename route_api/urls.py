from django.urls import path
from . import views

urlpatterns = [
    path('plan-route/', views.route_planner, name='route_planner'),
]