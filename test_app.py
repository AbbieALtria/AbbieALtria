import unittest
import io
import os
from app import app, submitted_applications # Import the Flask app and the in-memory store

class TestAppSubmission(unittest.TestCase):

    def setUp(self):
        """Set up test variables."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # If using Flask-WTF, disable CSRF for tests
        app.config['UPLOAD_FOLDER'] = 'test_uploads' # Use a separate upload folder for tests
        self.client = app.test_client()

        # Ensure the test upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Reset in-memory store before each test
        submitted_applications.clear()


    def tearDown(self):
        """Clean up after tests."""
        # Remove test upload folder and its contents
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for f in os.listdir(app.config['UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
            os.rmdir(app.config['UPLOAD_FOLDER'])


    def post_form_data(self, data, content_type='multipart/form-data'):
        """Helper function to post form data."""
        return self.client.post('/submit_application', data=data, content_type=content_type)

    def test_empty_submission_shows_errors(self):
        """Test that submitting an empty form shows multiple errors."""
        response = self.post_form_data({})
        self.assertEqual(response.status_code, 200) # Should re-render the form
        
        # Check for presence of key required field errors in the response data
        response_data_str = response.data.decode('utf-8')
        self.assertIn("Full Name is required.", response_data_str)
        self.assertIn("Date of Birth is required.", response_data_str)
        self.assertIn("Mobile number is required.", response_data_str)
        self.assertIn("Email is required.", response_data_str)
        self.assertIn("Country is required.", response_data_str)
        # Education has no "at least one" rule, but the first entry's fields are required
        self.assertIn("School Name is required.", response_data_str) # Assuming one default entry
        self.assertIn("At least one language entry is required.", response_data_str)
        self.assertIn("Resume is required.", response_data_str)
        self.assertIn("Photo is required.", response_data_str)
        self.assertIn("Join Availability is required.", response_data_str)

    def test_personal_info_validations(self):
        """Test various validations in the Personal Information section."""
        # Test Full Name required
        data = {"dob": "2000-01-01", "mobile": "1234567890", "email": "test@example.com"}
        response = self.post_form_data(data)
        self.assertIn("Full Name is required.", response.data.decode())

        # Test DOB under 18
        data = {"fullName": "Test User", "dob": "2010-01-01", "mobile": "1234567890", "email": "test@example.com"}
        response = self.post_form_data(data)
        self.assertIn("Applicant must be 18 years or older.", response.data.decode())

        # Test invalid email format
        data = {"fullName": "Test User", "dob": "2000-01-01", "mobile": "1234567890", "email": "test"}
        response = self.post_form_data(data)
        self.assertIn("Invalid email format.", response.data.decode())

        # Test non-numeric mobile
        data = {"fullName": "Test User", "dob": "2000-01-01", "mobile": "abcdefghij", "email": "test@example.com"}
        response = self.post_form_data(data)
        self.assertIn("Mobile number must be numeric.", response.data.decode())

    def test_address_postal_code_validation(self):
        """Test Postal Code numeric validation."""
        # Provide minimal valid data for other required fields to isolate postal code test
        data = {
            "fullName": "Test User", "dob": "2000-01-01", "mobile": "1234567890", "email": "test@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Manila",
            "education[0][school_name]": "Test School", 
            "education[0][school_year_from]": "2015-01-01", 
            "education[0][school_year_to]": "2019-01-01", 
            "education[0][education_level]": "Bachelor's",
            "language[0][name]": "English", "language[0][fluency]": "Native",
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate",
            "postalCode": "abcde" # Invalid postal code
        }
        response = self.post_form_data(data)
        self.assertIn("Postal Code must be numeric if provided.", response.data.decode())

    def test_education_validations(self):
        """Test validations for the Education section."""
        # Test School Name required in the first default entry
        data = {
            "fullName": "Test User", "dob": "2000-01-01", "mobile": "1234567890", "email": "test@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Manila",
            # Missing education[0][school_name]
            "education[0][school_year_from]": "2015-01-01", 
            "education[0][school_year_to]": "2019-01-01", 
            "education[0][education_level]": "Bachelor's",
            "language[0][name]": "English", "language[0][fluency]": "Native",
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate"
        }
        response = self.post_form_data(data)
        self.assertIn("School Name is required.", response.data.decode())
        self.assertIn("errors.education", response.data.decode()) # Check if error is structured correctly

    def test_work_experience_date_validations(self):
        """Test date validations for Work Experience section."""
        # Test 'To Date' must be after 'From Date'
        data_to_after_from = {
            "fullName": "Test User", "dob": "1990-01-01", "mobile": "1234567890", "email": "test@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Manila",
            "education[0][school_name]": "Test School", "education[0][school_year_from]": "2010-01-01", 
            "education[0][school_year_to]": "2014-01-01", "education[0][education_level]": "Bachelor's",
            "language[0][name]": "English", "language[0][fluency]": "Native",
            "experience[0][company_name]": "Test Corp", "experience[0][job_title]": "Developer",
            "experience[0][from_date]": "2015-06-01", "experience[0][to_date]": "2015-01-01", # Invalid dates
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate"
        }
        response = self.post_form_data(data_to_after_from)
        self.assertIn("To Date must be after From Date.", response.data.decode())

        # Test 'From Date' cannot be before applicant turned 18
        data_from_before_18 = {
            "fullName": "Test User", "dob": "1990-01-01", "mobile": "1234567890", "email": "test@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Manila",
            "education[0][school_name]": "Test School", "education[0][school_year_from]": "2010-01-01", 
            "education[0][school_year_to]": "2014-01-01", "education[0][education_level]": "Bachelor's",
            "language[0][name]": "English", "language[0][fluency]": "Native",
            "experience[0][company_name]": "Test Corp", "experience[0][job_title]": "Developer",
            "experience[0][from_date]": "2007-01-01", # Applicant turns 18 in 2008-01-01
            "experience[0][to_date]": "2009-01-01",
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate"
        }
        response = self.post_form_data(data_from_before_18)
        self.assertIn("From Date cannot be before applicant turned 18 (2008-01-01).", response.data.decode())

    def test_language_validations(self):
        """Test 'at least one language' and individual entry validations."""
        # Test "at least one language required"
        data_no_lang = {
            "fullName": "Test User", "dob": "2000-01-01", "mobile": "1234567890", "email": "test@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Manila",
            "education[0][school_name]": "Test School", "education[0][school_year_from]": "2015-01-01", 
            "education[0][school_year_to]": "2019-01-01", "education[0][education_level]": "Bachelor's",
            # No language entries
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate"
        }
        response = self.post_form_data(data_no_lang)
        self.assertIn("At least one language entry is required.", response.data.decode())

        # Test language name required within an entry
        data_lang_name_missing = {
            "fullName": "Test User", "dob": "2000-01-01", "mobile": "1234567890", "email": "test@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Manila",
            "education[0][school_name]": "Test School", "education[0][school_year_from]": "2015-01-01", 
            "education[0][school_year_to]": "2019-01-01", "education[0][education_level]": "Bachelor's",
            "language[0][fluency]": "Native", # Missing language[0][name]
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate"
        }
        response = self.post_form_data(data_lang_name_missing)
        self.assertIn("Language is required.", response.data.decode())
        self.assertIn("errors.language", response.data.decode())


    def test_social_media_validation(self):
        """Test Social Media URL validation."""
        data = {
            "fullName": "Test User", "dob": "2000-01-01", "mobile": "1234567890", "email": "test@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Manila",
            "education[0][school_name]": "Test School", "education[0][school_year_from]": "2015-01-01", 
            "education[0][school_year_to]": "2019-01-01", "education[0][education_level]": "Bachelor's",
            "language[0][name]": "English", "language[0][fluency]": "Native",
            "social_media[0][platform]": "LinkedIn", 
            "social_media[0][profile_link]": "invalid-url", # Invalid URL
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate"
        }
        response = self.post_form_data(data)
        self.assertIn("Invalid URL format. Please include http:// or https://.", response.data.decode())

    def test_other_fields_validations(self):
        """Test validations for Resume, Photo, and Join Availability."""
        base_data = {
            "fullName": "Test User", "dob": "2000-01-01", "mobile": "1234567890", "email": "test@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Manila",
            "education[0][school_name]": "Test School", "education[0][school_year_from]": "2015-01-01", 
            "education[0][school_year_to]": "2019-01-01", "education[0][education_level]": "Bachelor's",
            "language[0][name]": "English", "language[0][fluency]": "Native"
        }

        # Test Resume required
        data_no_resume = base_data.copy()
        data_no_resume.update({
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate"
        })
        response = self.post_form_data(data_no_resume)
        self.assertIn("Resume is required.", response.data.decode())

        # Test Resume invalid file type
        data_resume_invalid_type = base_data.copy()
        data_resume_invalid_type.update({
            "resume": (io.BytesIO(b"dummy resume content"), "resume.txt"), # Invalid type
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png"),
            "join_availability": "Immediate"
        })
        response = self.post_form_data(data_resume_invalid_type)
        self.assertIn("Invalid resume file type. Allowed: .pdf, .doc, .docx.", response.data.decode())

        # Test Photo required
        data_no_photo = base_data.copy()
        data_no_photo.update({
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "join_availability": "Immediate"
        })
        response = self.post_form_data(data_no_photo)
        self.assertIn("Photo is required.", response.data.decode())

        # Test Photo invalid file type
        data_photo_invalid_type = base_data.copy()
        data_photo_invalid_type.update({
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.gif"), # Invalid type
            "join_availability": "Immediate"
        })
        response = self.post_form_data(data_photo_invalid_type)
        self.assertIn("Invalid photo file type. Allowed: .jpg, .jpeg, .png.", response.data.decode())

        # Test Join Availability required
        data_no_join = base_data.copy()
        data_no_join.update({
            "resume": (io.BytesIO(b"dummy resume content"), "resume.pdf"),
            "photo": (io.BytesIO(b"dummy photo content"), "photo.png")
        })
        response = self.post_form_data(data_no_join)
        self.assertIn("Join Availability is required.", response.data.decode())

    def test_duplicate_submission(self):
        """Test that submitting the same email/mobile shows a duplicate error."""
        valid_data = {
            "fullName": "Original User", "dob": "1995-05-05", "mobile": "09171234567", "email": "original@example.com",
            "country": "Philippines", "province": "Cebu", "city": "Cebu City",
            "education[0][school_name]": "Cebu Uni", "education[0][school_year_from]": "2010-01-01",
            "education[0][school_year_to]": "2014-01-01", "education[0][education_level]": "Bachelor's",
            "language[0][name]": "English", "language[0][fluency]": "Native",
            "language[1][name]": "Tagalog", "language[1][fluency]": "Native",
            "resume": (io.BytesIO(b"valid resume"), "my_resume.pdf"),
            "photo": (io.BytesIO(b"valid photo"), "my_photo.jpg"),
            "join_availability": "1 week"
        }
        # First submission - should be successful
        response1 = self.post_form_data(valid_data.copy()) # Use .copy() if data is modified by post_form_data
        self.assertEqual(response1.status_code, 302) # Redirect to success
        self.assertEqual(len(submitted_applications), 1)

        # Second submission with same email
        duplicate_email_data = valid_data.copy()
        duplicate_email_data["fullName"] = "Duplicate Email User"
        duplicate_email_data["mobile"] = "09177654321" # Different mobile
        response2 = self.post_form_data(duplicate_email_data)
        self.assertEqual(response2.status_code, 200)
        self.assertIn("An application with this email or mobile number already exists.", response2.data.decode())
        self.assertEqual(len(submitted_applications), 1) # Should not have added

        # Third submission with same mobile
        duplicate_mobile_data = valid_data.copy()
        duplicate_mobile_data["fullName"] = "Duplicate Mobile User"
        duplicate_mobile_data["email"] = "otheroriginal@example.com" # Different email
        response3 = self.post_form_data(duplicate_mobile_data)
        self.assertEqual(response3.status_code, 200)
        self.assertIn("An application with this email or mobile number already exists.", response3.data.decode())
        self.assertEqual(len(submitted_applications), 1)


    def test_successful_submission(self):
        """Test a complete valid submission."""
        full_valid_data = {
            "fullName": "Valid Applicant", "dob": "1992-02-02", "gender": "Female", "maritalStatus": "Single",
            "mobile": "09181112233", "viber": "09181112233", "whatsapp": "09181112233", "email": "valid@example.com",
            "country": "Philippines", "province": "Metro Manila", "city": "Quezon City", "barangay": "Diliman", "postalCode": "1101",
            "education[0][school_name]": "UP Diliman", "education[0][subject_studied]": "Computer Science",
            "education[0][school_year_from]": "2010-06-01", "education[0][school_year_to]": "2014-03-31", "education[0][education_level]": "Bachelor's",
            "education[1][school_name]": "PHS", "education[1][subject_studied]": "General",
            "education[1][school_year_from]": "2006-06-01", "education[1][school_year_to]": "2010-03-31", "education[1][education_level]": "High School",
            "experience[0][company_name]": "Tech Solutions Inc.", "experience[0][job_title]": "Software Engineer",
            "experience[0][from_date]": "2015-04-01", "experience[0][to_date]": "2020-12-31",
            "language[0][name]": "English", "language[0][fluency]": "Native",
            "language[1][name]": "Tagalog", "language[1][fluency]": "Native",
            "social_media[0][platform]": "LinkedIn", "social_media[0][profile_link]": "http://linkedin.com/in/validapplicant",
            "resume": (io.BytesIO(b"This is a PDF resume."), "applicant_resume.pdf"),
            "photo": (io.BytesIO(b"This is a JPG photo."), "applicant_photo.jpg"),
            "join_availability": "Immediate"
        }
        response = self.post_form_data(full_valid_data)
        self.assertEqual(response.status_code, 302, f"Expected redirect, got errors: {response.data.decode()}")
        self.assertIn('/submission_success', response.location)
        self.assertEqual(len(submitted_applications), 1)
        
        # Verify some data in the stored application
        stored_app = submitted_applications[0]
        self.assertEqual(stored_app['fullName'], "Valid Applicant")
        self.assertEqual(stored_app['email'], "valid@example.com")
        self.assertTrue('resume_filename' in stored_app) # Check if filename was stored
        self.assertTrue('photo_filename' in stored_app)
        self.assertEqual(len(stored_app['education']), 2)
        self.assertEqual(stored_app['education'][0]['school_name'], "UP Diliman")


if __name__ == '__main__':
    unittest.main()
