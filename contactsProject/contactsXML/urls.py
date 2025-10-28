# contactsXML/urls.py

from django.urls import path
from . import views

app_name = 'contactsXML'  # ← ВАЖНО! для {% url 'contactsXML:list_files' %}

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_contact, name='add_contact'),
    path('upload/', views.upload_file, name='upload_file'),
    path('list/', views.list_files, name='list_files'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
]