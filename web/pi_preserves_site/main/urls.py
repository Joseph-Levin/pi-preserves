from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/',  auth_views.LoginView.as_view()),
    path('register/', views.register_view),
    path('logout/', views.logout_view),
    path('upload/', views.upload_files, name='upload files'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('view/<int:id>', views.view_file, name='view_file'),
    path('download/<int:id>', views.download_file_request, name='download_file_request'),
    path('delete/<int:id>', views.delete_file, name='delete_file'),
    path('view_files/', views.view_files, name='view files'),
    # path('<str:filepath>/', views.download_file, name='download'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)