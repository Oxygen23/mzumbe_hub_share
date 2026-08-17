#from django.shortcuts import render

# Create your views here.

# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse
from .models import Document
from .forms import RegisterForm, LoginForm, DocumentForm, SearchForm
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_protect  

# ============ AUTHENTICATION VIEWS ============
@csrf_protect
def register(request):
    """Registration page."""
    if request.user.is_authenticated:
        return redirect('AppTodo:home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account has been created.")
            return redirect('AppTodo:home')
    else:
        form = RegisterForm()
    
    return render(request, 'core/register.html', {'form': form})
@csrf_protect
def login_view(request):
    """Login page."""
    if request.user.is_authenticated:
        return redirect('AppTodo:home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back {username}!")
                return redirect('AppTodo:home')
        messages.error(request, "Username or password is incorrect.")
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})

# ============ DOCUMENT CRUD OPERATIONS ============

@login_required
def home(request):
    """Home page - display all documents."""
    documents = Document.objects.filter(is_approved=True).order_by('-uploaded_at')
    
    # Search functionality
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        doc_type = search_form.cleaned_data.get('document_type')
        
        if query:
            documents = documents.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(course_name__icontains=query) |
                Q(course_code__icontains=query) |
                Q(tags__icontains=query)
            )
        
        if doc_type:
            documents = documents.filter(document_type=doc_type)
    
    # Pagination
    paginator = Paginator(documents, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_documents = Document.objects.filter(is_approved=True).count()
    my_documents = Document.objects.filter(uploaded_by=request.user).count()
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_documents': total_documents,
        'my_documents': my_documents,
        'document_types': Document.DOCUMENT_TYPES,
    }
    return render(request, 'core/home.html', context)

@login_required
def document_detail(request, pk):
    """Onyesha document moja"""
    document = get_object_or_404(Document, pk=pk, is_approved=True)
    
    # Increment view count
    document.view_count += 1
    document.save()
    
    # Get related documents
    related_docs = Document.objects.filter(
        Q(course_code=document.course_code) | Q(tags__icontains=document.tags),
        is_approved=True
    ).exclude(pk=document.pk)[:5]
    
    context = {
        'document': document,
        'related_docs': related_docs,
    }
    return render(request, 'core/document_detail.html', context)

@login_required
def document_create(request):
    """Create a new document."""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.is_approved = True  # Auto-approve
            document.save()
            messages.success(request, f"Document '{document.title}' uploaded successfully!")
            return redirect('AppTodo:document_detail', pk=document.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DocumentForm()
    
    return render(request, 'core/document_form.html', {
        'form': form,
        'title': 'Upload New Document',
        'button_text': 'Upload',
        'is_edit': False
    })

@login_required
def document_edit(request, pk):
    """Edit an existing document."""
    document = get_object_or_404(Document, pk=pk, uploaded_by=request.user)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, f"Document '{document.title}' updated successfully!")
            return redirect('AppTodo:document_detail', pk=document.pk)
    else:
        form = DocumentForm(instance=document)
    
    return render(request, 'core/document_form.html', {
        'form': form,
        'title': 'Edit Document',
        'button_text': 'Save',
        'is_edit': True,
        'document': document
    })

@login_required
def document_delete(request, pk):
    """Delete a document."""
    document = get_object_or_404(Document, pk=pk, uploaded_by=request.user)
    
    if request.method == 'POST':
        # Delete file from server
        if document.file and os.path.exists(document.file.path):
            os.remove(document.file.path)
        document.delete()
        messages.success(request, f"Document '{document.title}' deleted successfully!")
        return redirect('AppTodo:home')
    
    return render(request, 'core/document_confirm_delete.html', {'document': document})

@login_required
def document_download(request, pk):
    """Download a document."""
    document = get_object_or_404(Document, pk=pk, is_approved=True)
    
    # Increment download count
    document.download_count += 1
    document.save()
    
    # Return file
    if document.file and os.path.exists(document.file.path):
        response = FileResponse(open(document.file.path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{document.file.name}"'
        return response
    else:
        messages.error(request, "File not found.")
        return redirect('AppTodo:document_detail', pk=document.pk)

@login_required
def my_documents(request):
    """Show only my documents."""
    documents = Document.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    
    paginator = Paginator(documents, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'is_my_docs': True
    }
    return render(request, 'core/my_documents.html', context)



@login_required
def document_detail(request, pk):
    """Onyesha document moja"""
    from django.shortcuts import get_object_or_404
    document = get_object_or_404(Document, pk=pk)
    
    # Ongeza view count
    document.view_count += 1
    document.save()
    
    context = {
        'document': document,
    }
    return render(request, 'core/document_detail.html', context)


def csrf_failure(request, reason=""):
    return render(request, 'core/csrf_failure.html', {'reason': reason})
