from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date
import re

app = Flask(__name__)

# In-memory "database" for submitted applications
submitted_applications = []

def calculate_age(born_str):
    try:
        born = datetime.strptime(born_str, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age
    except ValueError:
        return None

@app.route('/')
def index():
    return render_template('index.html', errors={}, form_data={})

@app.route('/submit_application', methods=['POST'])
def submit_application():
    form_data = request.form
    errors = {}
    # Make form_data mutable from the start for easier updates
    mutable_form_data = form_data.to_dict() if hasattr(form_data, 'to_dict') else dict(form_data)

    # Full Name
    full_name = form_data.get('fullName', '').strip()
    if not full_name:
        errors['fullName'] = 'Full Name is required.'

    # Date of Birth
    dob_str = form_data.get('dob', '')
    if not dob_str:
        errors['dob'] = 'Date of Birth is required.'
    else:
        age = calculate_age(dob_str)
        if age is None:
            errors['dob'] = 'Invalid Date of Birth format.'
        elif age < 18:
            errors['dob'] = 'Applicant must be 18 years or older.'

    # Gender - No server-side validation needed as it's a select
    # Marital Status - No server-side validation needed as it's a select

    # Mobile
    mobile = form_data.get('mobile', '').strip()
    if not mobile:
        errors['mobile'] = 'Mobile number is required.'
    elif not mobile.isdigit():
        errors['mobile'] = 'Mobile number must be numeric.'

    # Viber
    viber = form_data.get('viber', '').strip()
    if viber and not viber.isdigit():
        errors['viber'] = 'Viber number must be numeric if provided.'

    # WhatsApp
    whatsapp = form_data.get('whatsapp', '').strip()
    if whatsapp and not whatsapp.isdigit():
        errors['whatsapp'] = 'WhatsApp number must be numeric if provided.'

    # Email
    email = form_data.get('email', '').strip()
    if not email:
        errors['email'] = 'Email is required.'
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email): # Basic email format
        errors['email'] = 'Invalid email format.'

    # Address Section
    country = form_data.get('country', '').strip()
    if not country: # Country is required as per instruction
        errors['country'] = 'Country is required.'

    province = form_data.get('province', '').strip()
    # Basic check, actual validation depends on dynamic content
    if country == "Philippines" and not province: # Province might be considered required if Philippines is selected
        errors['province'] = 'Province is required.'

    city = form_data.get('city', '').strip()
    # Basic check, actual validation depends on dynamic content
    if province and not city: # City might be considered required if a province is selected
         errors['city'] = 'City/Municipality is required.'

    # Barangay - optional, no specific validation rules given other than it's a text input
    barangay = form_data.get('barangay', '').strip()

    # Postal Code
    postal_code = form_data.get('postalCode', '').strip()
    if postal_code and not postal_code.isdigit():
        errors['postalCode'] = 'Postal Code must be numeric if provided.'

    # Education Section
    education_entries = []
    education_errors = [] # This will be a list of dictionaries
    i = 0
    while True:
        # Check for a required field like school_name to determine if the entry exists
        school_name_key = f'education[{i}][school_name]'
        if school_name_key not in form_data:
            break

        entry_errors = {}
        school_name = form_data.get(school_name_key, '').strip()
        subject_studied = form_data.get(f'education[{i}][subject_studied]', '').strip()
        school_year_from_str = form_data.get(f'education[{i}][school_year_from]', '').strip()
        school_year_to_str = form_data.get(f'education[{i}][school_year_to]', '').strip()
        education_level = form_data.get(f'education[{i}][education_level]', '').strip()

        if not school_name:
            entry_errors['school_name'] = 'School Name is required.'
        if not school_year_from_str:
            entry_errors['school_year_from'] = 'School Year (From) is required.'
        # Add more date validation if needed (e.g., format, From < To)
        if not school_year_to_str:
            entry_errors['school_year_to'] = 'School Year (To) is required.'
        if not education_level:
            entry_errors['education_level'] = 'Education Level is required.'

        education_entries.append({
            'school_name': school_name,
            'subject_studied': subject_studied,
            'school_year_from': school_year_from_str,
            'school_year_to': school_year_to_str,
            'education_level': education_level
        })
        
        if entry_errors:
            education_errors.append(entry_errors)
        else:
            education_errors.append({}) # Append an empty dict if no errors for this entry

        i += 1
    
    if any(education_errors): # Check if any of the entry error dicts are non-empty
        errors['education'] = education_errors
    
    # Add education_entries to form_data for repopulation
    # Personal Information (already populates mutable_form_data)
    # Full Name
    full_name = mutable_form_data.get('fullName', '').strip()
    if not full_name:
        errors['fullName'] = 'Full Name is required.'

    # Date of Birth
    dob_str = mutable_form_data.get('dob', '')
    applicant_dob_date = None # Define here for wider scope for experience validation
    if not dob_str:
        errors['dob'] = 'Date of Birth is required.'
    else:
        age = calculate_age(dob_str)
        if age is None:
            errors['dob'] = 'Invalid Date of Birth format.'
        elif age < 18:
            errors['dob'] = 'Applicant must be 18 years or older.'
        else:
            try:
                applicant_dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                 pass # Error already caught by calculate_age or initial check

    # Mobile
    mobile = mutable_form_data.get('mobile', '').strip()
    if not mobile:
        errors['mobile'] = 'Mobile number is required.'
    elif not mobile.isdigit():
        errors['mobile'] = 'Mobile number must be numeric.'

    # Viber
    viber = mutable_form_data.get('viber', '').strip()
    if viber and not viber.isdigit():
        errors['viber'] = 'Viber number must be numeric if provided.'

    # WhatsApp
    whatsapp = mutable_form_data.get('whatsapp', '').strip()
    if whatsapp and not whatsapp.isdigit():
        errors['whatsapp'] = 'WhatsApp number must be numeric if provided.'

    # Email
    email = mutable_form_data.get('email', '').strip()
    if not email:
        errors['email'] = 'Email is required.'
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors['email'] = 'Invalid email format.'

    # Address Section
    country = mutable_form_data.get('country', '').strip()
    if not country:
        errors['country'] = 'Country is required.'
    province = mutable_form_data.get('province', '').strip()
    if country == "Philippines" and not province:
        errors['province'] = 'Province is required.'
    city = mutable_form_data.get('city', '').strip()
    if province and not city:
         errors['city'] = 'City/Municipality is required.'
    postal_code = mutable_form_data.get('postalCode', '').strip()
    if postal_code and not postal_code.isdigit():
        errors['postalCode'] = 'Postal Code must be numeric if provided.'

    # Education Section
    education_entries = []
    education_errors = []
    i = 0
    while True:
        school_name_key = f'education[{i}][school_name]'
        if school_name_key not in mutable_form_data and f'education[{i}][education_level]' not in mutable_form_data : # Check a couple of fields
             is_empty_entry = True
             for field_key_suffix in ['school_name', 'subject_studied', 'school_year_from', 'school_year_to', 'education_level']:
                 if mutable_form_data.get(f'education[{i}][{field_key_suffix}]', '').strip():
                     is_empty_entry = False
                     break
             if is_empty_entry:
                 break
        
        entry_errors = {}
        school_name = mutable_form_data.get(school_name_key, '').strip()
        subject_studied = mutable_form_data.get(f'education[{i}][subject_studied]', '').strip()
        school_year_from_str = mutable_form_data.get(f'education[{i}][school_year_from]', '').strip()
        school_year_to_str = mutable_form_data.get(f'education[{i}][school_year_to]', '').strip()
        education_level = mutable_form_data.get(f'education[{i}][education_level]', '').strip()

        if not school_name: entry_errors['school_name'] = 'School Name is required.'
        if not school_year_from_str: entry_errors['school_year_from'] = 'School Year (From) is required.'
        if not school_year_to_str: entry_errors['school_year_to'] = 'School Year (To) is required.'
        if not education_level: entry_errors['education_level'] = 'Education Level is required.'
        
        current_entry_data = {
            'school_name': school_name, 'subject_studied': subject_studied,
            'school_year_from': school_year_from_str, 'school_year_to': school_year_to_str,
            'education_level': education_level
        }
        education_entries.append(current_entry_data)
        if entry_errors: education_errors.append(entry_errors)
        else: education_errors.append({})
        i += 1
        if i > 50: break
    if any(education_errors): errors['education'] = education_errors
    mutable_form_data['education'] = education_entries


    # Work Experience Section
    experience_entries = []
    experience_errors = []
    j = 0
    # applicant_dob_date is already defined and parsed from Personal Info section
    while True:
        company_name_key = f'experience[{j}][company_name]'
        if company_name_key not in mutable_form_data and f'experience[{j}][job_title]' not in mutable_form_data:
            is_empty_entry = True
            for field_key_suffix in ['company_name', 'job_title', 'from_date', 'to_date']:
                if mutable_form_data.get(f'experience[{j}][{field_key_suffix}]', '').strip():
                    is_empty_entry = False
                    break
            if is_empty_entry: break

        entry_errors = {}
        company_name = mutable_form_data.get(company_name_key, '').strip()
        job_title = mutable_form_data.get(f'experience[{j}][job_title]', '').strip()
        from_date_str = mutable_form_data.get(f'experience[{j}][from_date]', '').strip()
        to_date_str = mutable_form_data.get(f'experience[{j}][to_date]', '').strip()
        from_date, to_date = None, None
        if from_date_str:
            try: from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            except ValueError: entry_errors['from_date'] = 'Invalid From Date format.'
        if to_date_str:
            try: to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            except ValueError: entry_errors['to_date'] = 'Invalid To Date format.'
        if from_date and to_date and from_date > to_date: entry_errors['to_date'] = 'To Date must be after From Date.'
        if from_date and applicant_dob_date:
            applicant_18th_birthday = applicant_dob_date.replace(year=applicant_dob_date.year + 18)
            if from_date < applicant_18th_birthday:
                entry_errors['from_date'] = f'From Date cannot be before applicant turned 18 ({applicant_18th_birthday.strftime("%Y-%m-%d")}).'
        elif from_date_str and not applicant_dob_date and 'dob' not in errors:
             entry_errors['from_date'] = 'Cannot validate From Date without applicant Date of Birth.'
        
        current_exp_data = {'company_name': company_name, 'job_title': job_title, 'from_date': from_date_str, 'to_date': to_date_str}
        if company_name or job_title or from_date_str or to_date_str or entry_errors:
            experience_entries.append(current_exp_data)
            if entry_errors: experience_errors.append(entry_errors)
            else: experience_errors.append({})
        j += 1
        if j > 50: break
    if any(experience_errors): errors['experience'] = experience_errors
    mutable_form_data['experience'] = experience_entries

    # Language Section
    language_entries = []
    language_errors = []
    k = 0
    while True:
        lang_name_key = f'language[{k}][name]'
        if lang_name_key not in mutable_form_data and f'language[{k}][fluency]' not in mutable_form_data:
            is_empty_entry = True
            for field_key_suffix in ['name', 'fluency']:
                 if mutable_form_data.get(f'language[{k}][{field_key_suffix}]', '').strip():
                     is_empty_entry = False
                     break
            if is_empty_entry: break
        entry_errors = {}
        lang_name = mutable_form_data.get(lang_name_key, '').strip()
        fluency = mutable_form_data.get(f'language[{k}][fluency]', '').strip()
        if not lang_name: entry_errors['name'] = 'Language is required.'
        if not fluency: entry_errors['fluency'] = 'Fluency is required.'
        
        current_lang_data = {'name': lang_name, 'fluency': fluency}
        if lang_name or fluency or entry_errors:
            language_entries.append(current_lang_data)
            if entry_errors: language_errors.append(entry_errors)
            else: language_errors.append({})
        k += 1
        if k > 50: break
    if not language_entries: errors['language_general'] = 'At least one language entry is required.'
    elif any(language_errors): errors['language'] = language_errors
    mutable_form_data['language'] = language_entries

    # Social Media Section
    social_media_entries = []
    social_media_errors = []
    sm_idx = 0
    url_pattern = re.compile(r'^(?:http|ftp)s?://.*?$', re.IGNORECASE)
    while True:
        platform_key = f'social_media[{sm_idx}][platform]'
        if platform_key not in mutable_form_data and f'social_media[{sm_idx}][profile_link]' not in mutable_form_data:
            is_empty_entry = True
            for field_key_suffix in ['platform', 'profile_link']:
                if mutable_form_data.get(f'social_media[{sm_idx}][{field_key_suffix}]', '').strip():
                    is_empty_entry = False
                    break
            if is_empty_entry: break
        entry_errors = {}
        platform = mutable_form_data.get(platform_key, '').strip()
        profile_link = mutable_form_data.get(f'social_media[{sm_idx}][profile_link]', '').strip()
        if platform or profile_link:
            if not platform: entry_errors['platform'] = 'Platform is required if adding a social media account.'
            if profile_link and not url_pattern.match(profile_link):
                entry_errors['profile_link'] = 'Invalid URL format. Please include http:// or https://.'
            current_sm_data = {'platform': platform, 'profile_link': profile_link}
            social_media_entries.append(current_sm_data)
            if entry_errors: social_media_errors.append(entry_errors)
            else: social_media_errors.append({})
        sm_idx += 1
        if sm_idx > 50: break
    if any(social_media_errors): errors['social_media'] = social_media_errors
    mutable_form_data['social_media'] = social_media_entries
    
    # Other Information Section
    UPLOAD_FOLDER = 'uploads'
    if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}
    ALLOWED_PHOTO_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    join_availability = mutable_form_data.get('join_availability', '').strip()
    if not join_availability: errors['join_availability'] = 'Join Availability is required.'
    
    resume_file = request.files.get('resume')
    if not resume_file or not resume_file.filename: errors['resume'] = 'Resume is required.'
    elif not allowed_file(resume_file.filename, ALLOWED_RESUME_EXTENSIONS):
        errors['resume_type'] = 'Invalid resume file type. Allowed: .pdf, .doc, .docx.'
    else:
        try:
            resume_filename = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))
            mutable_form_data['resume_filename'] = resume_filename
        except Exception as e: errors['resume_save'] = f"Could not save resume: {e}"

    photo_file = request.files.get('photo')
    if not photo_file or not photo_file.filename: errors['photo'] = 'Photo is required.'
    elif not allowed_file(photo_file.filename, ALLOWED_PHOTO_EXTENSIONS):
        errors['photo_type'] = 'Invalid photo file type. Allowed: .jpg, .jpeg, .png.'
    else:
        try:
            photo_filename = secure_filename(photo_file.filename)
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            mutable_form_data['photo_filename'] = photo_filename
        except Exception as e: errors['photo_save'] = f"Could not save photo: {e}"

    # --- Duplicate Check ---
    if not errors: # Only check for duplicates if all other validations passed
        current_email = mutable_form_data.get('email')
        current_mobile = mutable_form_data.get('mobile')
        for app_data in submitted_applications:
            if app_data.get('email') == current_email or app_data.get('mobile') == current_mobile:
                errors['duplicate'] = "An application with this email or mobile number already exists."
                break 
    
    if errors:
        return render_template('index.html', errors=errors, form_data=mutable_form_data)
    else:
        # Add to our in-memory "database"
        submitted_applications.append(mutable_form_data.copy()) # Store a copy
        return redirect(url_for('submission_success'))

@app.route('/submission_success')
def submission_success():
    return render_template('success.html')

if __name__ == '__main__':
    import os
    from werkzeug.utils import secure_filename
    app.run(debug=True)
