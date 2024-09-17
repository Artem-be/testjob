from django.urls import path
from .views import index, home, download_file, oauth_register, oauth_callback

urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('download/', download_file, name='download_file'),
    path('oauth/register/', oauth_register, name='oauth_register'),
    path('oauth/callback/', oauth_callback, name='oauth_callback'),
]