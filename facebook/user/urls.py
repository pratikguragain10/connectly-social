from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('home/', views.home, name='home'),

    # Auth
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('google_signup/', views.google_signup, name='google_signup'),

    # Profile & Feed
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Search & Friends
    path('search/', views.search_users, name='search_users'),
    path('friend/send/<int:user_id>/',views.send_friend_request,name='send_friend_request'),
    path('friend/cancel/<int:user_id>/',views.cancel_friend_request,name='cancel_friend_request'),
    path('friend/accept/<int:user_id>/',views.accept_friend,name='accept_friend'),
    path('friend/reject/<int:user_id>/',views.reject_friend_request,name='reject_friend_request'),
    path('friend/remove/<int:user_id>/',views.remove_friend,name='remove_friend'),

    # Post interactions
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    
    path('accounts/', include('allauth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

