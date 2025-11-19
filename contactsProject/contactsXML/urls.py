from django.urls import path
from . import views

app_name = 'contactsXML'

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_contact, name='add_contact'),
    path('upload/', views.upload_file, name='upload_file'),
    path('list/', views.list_contacts, name='list_contacts'),
    path('edit/<int:pk>/', views.edit_contact, name='edit_contact'),
    path('delete/<int:pk>/', views.delete_contact, name='delete_contact'),
    path('search/', views.search_contacts, name='search_contacts'),  # AJAX
    path('download/', views.download_file, name='download_file'),
]