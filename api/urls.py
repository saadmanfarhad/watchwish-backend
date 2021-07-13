from django.urls import path
from api import views

urlpatterns = [
    path('', views.welcome),
    path('register', views.register),
    path('login', views.login),
    path('login/social', views.login_social),
    path('user', views.user),
    path('user/about', views.post_user_about),
    path('media/status/<int:user_id>/<int:media_id>', views.media_status),
    path('watchlist/<int:user_id>', views.get_watchlist),
    path('watchedlist/<int:user_id>', views.get_watchedlist),
    path('watchlist', views.post_watchlist),
    path('watchlist/put', views.put_watchlist),
    path('review/<int:user_id>/<int:media_id>', views.get_review),
    path('review', views.post_review),
    path('review/put', views.put_review)
    # views.AQuery.as_view({'get':'do_get'})
    # path('snippets/<int:pk>/', views.snippet_detail),
]
