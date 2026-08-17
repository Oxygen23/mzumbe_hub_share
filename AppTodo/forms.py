# core/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Document
import os

class RegisterForm(UserCreationForm):
    """Registration form."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].help_text = None
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Barua pepe hii tayari imesajiliwa!")
        return email

class LoginForm(AuthenticationForm):
    """Login form."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = field

class DocumentForm(forms.ModelForm):
    """Form for creating/editing a document."""
    
    class Meta:
        model = Document
        fields = [
            'title', 'description', 'file', 'document_type',
            'course_code', 'course_name', 'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter document title...'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Briefly describe what this document is about...'
            }),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'course_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: CS101'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Programming Fundamentals'}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'programming, python, basics'
            }),
        }
        labels = {
            'title': 'Document Title *',
            'description': 'Description *',
            'file': 'File *',
            'document_type': 'Document Type',
            'course_code': 'Course Code',
            'course_name': 'Course Name',
            'tags': 'Keywords',
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check size (max 20MB)
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError("File is too large. Allowed size is up to 20MB.")
            
            # Check file type
            allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip', '.rar']
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f"File type '{ext}' is not allowed. "
                    f"Allowed types: {', '.join(allowed_extensions)}"
                )
        return file

class SearchForm(forms.Form):
    """Search form."""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search documents by title or description...'
        })
    )
    document_type = forms.ChoiceField(
        choices=[('', 'All')] + Document.DOCUMENT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )