from django.contrib import admin
from .models import JobPosting

class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'department', 'location', 'deadline_at', 'is_active', 'created_at')
    search_fields = ('job_title', 'department', 'location')
    list_filter = ('is_active', 'department', 'location')
    filter_horizontal = ('assigned_interviewers',)

admin.site.register(JobPosting, JobPostingAdmin)
