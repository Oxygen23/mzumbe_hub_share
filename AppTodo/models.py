#from django.db import models

# Create your models here.

# core/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

class Document(models.Model):
    """Document model."""
    DOCUMENT_TYPES = [
        ('NOTES', 'Study Notes'),
        ('PAST_PAPER', 'Past Paper'),
        ('ASSIGNMENT', 'Assignment'),
        ('BOOK', 'Book'),
        ('OTHER', 'Other'),
    ]
    
    # Required fields (title and description)
    title = models.CharField(max_length=200, verbose_name="Document Title")
    description = models.TextField(verbose_name="Document Description")
    
    # File
    file = models.FileField(
        upload_to='documents/%Y/%m/%d/', 
        verbose_name="File",
        help_text="Allowed file types: PDF, DOC, DOCX, PPT, PPTX, TXT"
    )
    file_size = models.IntegerField(blank=True, null=True, verbose_name="File Size (KB)")
    
    # Metadata
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='OTHER',
        verbose_name="Document Type"
    )
    
    # Course information
    course_code = models.CharField(max_length=20, blank=True, verbose_name="Course Code")
    course_name = models.CharField(max_length=100, blank=True, verbose_name="Course Name")
    
    # Tags for search
    tags = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Separate with commas, e.g.: programming, python, database",
        verbose_name="Keywords"
    )
    
    # Statistics
    download_count = models.IntegerField(default=0, verbose_name="Download Count")
    view_count = models.IntegerField(default=0, verbose_name="View Count")
    
    # Author
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name="Uploaded By"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    # Approval status
    is_approved = models.BooleanField(default=True, verbose_name="Approved")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Document"
        verbose_name_plural = "Documents"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Calculate file size (KB)
        if self.file:
            self.file_size = round(self.file.size / 1024, 2)  # KB
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """Get file extension."""
        if self.file:
            name, extension = os.path.splitext(self.file.name)
            return extension.lower()
        return ''
    
    def get_file_icon(self):
        """Get icon based on file extension."""
        ext = self.get_file_extension()
        icons = {
            '.pdf': 'fa-file-pdf',
            '.doc': 'fa-file-word',
            '.docx': 'fa-file-word',
            '.ppt': 'fa-file-powerpoint',
            '.pptx': 'fa-file-powerpoint',
            '.xls': 'fa-file-excel',
            '.xlsx': 'fa-file-excel',
            '.txt': 'fa-file-alt',
            '.zip': 'fa-file-archive',
            '.rar': 'fa-file-archive',
        }
        return icons.get(ext, 'fa-file')