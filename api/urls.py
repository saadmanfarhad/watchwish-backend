from django.urls import path
from api import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('login/social', views.login_social),
    path('user', views.get_user),
    # path('snippets/<int:pk>/', views.snippet_detail),
]
