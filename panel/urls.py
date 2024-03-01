from django.urls import path
from . import views

urlpatterns = [
    path('', views.testView, name='test'),
    path('login/', views.loginPage, name='login'),
]
