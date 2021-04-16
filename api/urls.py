from django.urls import path
from api import views

urlpatterns = [
    path('register', views.register),
    # path('snippets/<int:pk>/', views.snippet_detail),
]
