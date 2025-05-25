from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class JobPosting(models.Model):
    job_title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    job_description = models.TextField()
    location = models.CharField(max_length=100)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    schedule = models.CharField(max_length=50, blank=True, null=True)
    deadline_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    assigned_interviewers = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name='job_postings_assigned'
    )

    def __str__(self):
        return self.job_title

class Applicant(models.Model):
    JOIN_AVAILABILITY_CHOICES = [
        ('immediate', _('Immediate')),
        ('1_week', _('1 Week')),
        ('2_weeks', _('2 Weeks')),
        ('1_month', _('1 Month')),
    ]

    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applicants')
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    marital_status = models.CharField(max_length=30, blank=True, null=True)
    mobile_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    viber_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    street = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    facebook_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    tiktok_url = models.URLField(blank=True, null=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    photo_file = models.ImageField(upload_to='applicant_photos/', blank=True, null=True)
    join_availability = models.CharField(
        max_length=20,
        choices=JOIN_AVAILABILITY_CHOICES,
        blank=True,
        null=True
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='New')

    def __str__(self):
        return f"{self.full_name} - {self.job_posting.job_title}"

class Education(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='education_history')
    school = models.CharField(max_length=255)
    subject_studied = models.CharField(max_length=255)
    year_graduated = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.school} - {self.subject_studied} ({self.applicant.full_name})"

class Experience(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='experience_history')
    company = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company} ({self.applicant.full_name})"

class LanguageProficiency(models.Model):
    CEFR_LEVEL_CHOICES = [
        ('A1', 'A1'), ('A2', 'A2'),
        ('B1', 'B1'), ('B2', 'B2'),
        ('C1', 'C1'), ('C2', 'C2'),
    ]
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='languages')
    language_name = models.CharField(max_length=100)
    cefr_level = models.CharField(max_length=2, choices=CEFR_LEVEL_CHOICES)

    def __str__(self):
        return f"{self.language_name} ({self.cefr_level}) - {self.applicant.full_name}"
