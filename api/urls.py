from django.urls import path
from api import views

urlpatterns = [
    path('', views.welcome),
    path('register', views.register),
    path('login', views.login),
    path('login/social', views.login_social),
    path('user', views.user),
    path('user/<int:user_id>', views.get_user),
    path('user/about', views.post_user_about),
    path('media/status/<int:user_id>/<int:media_id>', views.media_status),
    path('watchlist/<int:user_id>', views.get_watchlist),
    path('watchedlist/<int:user_id>', views.get_watchedlist),
    path('watchlist', views.post_watchlist),
    path('watchlist/put', views.put_watchlist),
    path('review/<int:user_id>/<int:media_id>', views.get_review),
    path('review', views.post_review),
    path('review/put', views.put_review),
    path('friend/status/<int:user_id>/<int:friend_id>', views.get_friend_status),
    path('friend/request/send', views.send_friend_request),
    path('friend/request/accept', views.accept_friend_request)
    # views.AQuery.as_view({'get':'do_get'})
    # path('snippets/<int:pk>/', views.snippet_detail),
]
