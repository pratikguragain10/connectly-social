from django.urls import path  
from . import views  
from django.conf.urls.static import static  
from django.conf import settings  
  
urlpatterns = [  
   path('', views.homepage, name='homepage'),  
   path('signup/', views.signup, name='signup'),  
   path('login/', views.login, name='login'),  
   path('profile/', views.profile, name='profile'),  
   path('logout/', views.logout, name='logout'),  
   path('search/', views.search_users, name='search_users'),  
   path('add_friend/<int:user_id>/', views.add_friend, name='add_friend'),  
   path('friends/', views.friends, name='friends'),
   path('google_signup/', views.google_signup, name='google_signup'), 
   path('unfriend/<int:friend_id>/', views.unfriend, name='unfriend'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
