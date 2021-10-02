from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/',  auth_views.LoginView.as_view()),
    path('register/', views.register_view),
    path('logout/', views.logout_view),
    path('upload/', views.upload_files, name='upload files'),
    path('<int:id>', views.index, name='index'),
    path('view_files/', views.view_files, name='view files'),
]