from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import JobPosting, Applicant
from .forms import ApplicantForm, EducationFormSet, ExperienceFormSet, LanguageFormSet

def job_list(request):
    """
    Displays a list of active job postings.
    """
    job_postings = JobPosting.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'job_postings': job_postings
    }
    return render(request, 'jobs/job_list.html', context)

def submit_application(request, job_id):
    try:
        job_posting = JobPosting.objects.get(pk=job_id, is_active=True)
    except JobPosting.DoesNotExist:
        raise Http404("Job posting not found or is no longer active.")

    if request.method == 'POST':
        applicant_form = ApplicantForm(request.POST, request.FILES)
        education_formset = EducationFormSet(request.POST, prefix='education')
        experience_formset = ExperienceFormSet(request.POST, prefix='experience')
        language_formset = LanguageFormSet(request.POST, prefix='language')

        if (applicant_form.is_valid() and
            education_formset.is_valid() and
            experience_formset.is_valid() and
            language_formset.is_valid()):

            applicant = applicant_form.save(commit=False)
            applicant.job_posting = job_posting
            applicant.save() # Save the main applicant instance

            # Save formsets with the applicant instance
            education_formset.instance = applicant
            education_formset.save()

            experience_formset.instance = applicant
            experience_formset.save()

            language_formset.instance = applicant
            language_formset.save()

            return redirect(reverse('jobs:application_thank_you'))
        else:
            # Re-render with errors
            context = {
                'job_posting': job_posting,
                'applicant_form': applicant_form,
                'education_formset': education_formset,
                'experience_formset': experience_formset,
                'language_formset': language_formset,
            }
            return render(request, 'jobs/applicant_form.html', context)
    else: # GET request
        applicant_form = ApplicantForm()
        education_formset = EducationFormSet(prefix='education')
        experience_formset = ExperienceFormSet(prefix='experience')
        language_formset = LanguageFormSet(prefix='language')

    context = {
        'job_posting': job_posting,
        'applicant_form': applicant_form,
        'education_formset': education_formset,
        'experience_formset': experience_formset,
        'language_formset': language_formset,
    }
    return render(request, 'jobs/applicant_form.html', context)

def application_thank_you(request):
    return render(request, 'jobs/application_thank_you.html')

@login_required
def recruiter_dashboard(request):
    applicants = Applicant.objects.all().order_by('-applied_at')
    job_postings = JobPosting.objects.all().order_by('job_title') # For filter dropdown

    job_id_filter = request.GET.get('job_id', None)
    if job_id_filter and job_id_filter.isdigit():
        try:
            job_posting_filter = JobPosting.objects.get(pk=int(job_id_filter))
            applicants = applicants.filter(job_posting=job_posting_filter)
        except JobPosting.DoesNotExist:
            # Optionally, add a message if the job_id is invalid
            pass # Or handle as an error, e.g. applicants = Applicant.objects.none()

    context = {
        'applicants': applicants,
        'job_postings': job_postings,
        'selected_job_id': int(job_id_filter) if job_id_filter and job_id_filter.isdigit() else None,
    }
    return render(request, 'jobs/recruiter_dashboard.html', context)

@login_required
def applicant_detail(request, applicant_id):
    applicant = get_object_or_404(Applicant, pk=applicant_id)
    education_history = applicant.education_history.all()
    experience_history = applicant.experience_history.all()
    languages = applicant.languages.all()

    context = {
        'applicant': applicant,
        'education_history': education_history,
        'experience_history': experience_history,
        'languages': languages,
    }
    return render(request, 'jobs/applicant_detail.html', context)
