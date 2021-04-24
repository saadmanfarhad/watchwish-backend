from django.urls import path
from api import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('login/social', views.login_social),
    path('user', views.user),
    path('media/status/<int:user_id>/<int:media_id>', views.media_status),
    path('watchlist/<int:user_id>', views.get_watchlist),
    path('watchlist', views.post_watchlist),
    path('watchlist/put', views.put_watchlist)
    # views.AQuery.as_view({'get':'do_get'})
    # path('snippets/<int:pk>/', views.snippet_detail),
]
