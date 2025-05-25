from django import forms
from .models import Applicant, Education, Experience, LanguageProficiency, JobPosting

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        exclude = ['applied_at', 'status'] # job_posting will be set in the view

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'subject_studied', 'year_graduated']

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'job_title', 'start_date', 'end_date', 'description']

class LanguageForm(forms.ModelForm):
    class Meta:
        model = LanguageProficiency
        fields = ['language_name', 'cefr_level']

EducationFormSet = forms.inlineformset_factory(
    Applicant,
    Education,
    form=EducationForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True
)

ExperienceFormSet = forms.inlineformset_factory(
    Applicant,
    Experience,
    form=ExperienceForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True
)

LanguageFormSet = forms.inlineformset_factory(
    Applicant,
    LanguageProficiency,
    form=LanguageForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True
)
