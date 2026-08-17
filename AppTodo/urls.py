# core/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'AppTodo'

urlpatterns = [
    # Home & Documents
    path('', views.home, name='home'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    
    # CRUD Operations
    path('document/create/', views.document_create, name='document_create'),
    path('document/<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('document/<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('document/<int:pk>/download/', views.document_download, name='document_download'),
    
    # My Documents
    path('my-documents/', views.my_documents, name='my_documents'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='AppTodo:home'), name='logout'),
]