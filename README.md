ment projects, team assignments, and project documents. It implements robust security principles such as role-based access control, secure password handling, and defense in depth to ensure data integrity and user privacy.

Features
Core Functionality
Project Management:

Add/Remove Projects: Admins can add new game projects with a name, description, and initial deadline. Admins can also mark projects as "Completed."

View Projects: All authenticated users can view a list of active projects.

Team Assignment:

Assign Team Members: Project Leads can assign developers to their specific projects.

View Assigned Projects: Developers can see a list of projects they are currently assigned to.

Basic Asset & Resource Management:

Upload Project Documents: Admins and Project Leads can upload general project documents (e.g., design docs, meeting notes) associated with a project.

View Documents: All users assigned to a project can view its uploaded documents.

Privilege Separation (Role-Based Access Control)
Admin:

Can add/remove projects.

Can manage all user accounts (create, edit roles, delete).

Can upload documents for any project.

Project Lead:

Can assign developers to their projects.

Can upload documents for their projects.

Developer:

Can view projects they are assigned to.

Can access associated project documents.

Login Security
Robust Login System: Utilizes secure password hashing and storage (using bcrypt via Werkzeug.security).

MFA Implementation (Placeholder): The system is designed to allow for future Multi-Factor Authentication integration, though it is not fully implemented in this prototype.

Technologies Used
Backend: Python (Flask framework)

Database: SQLite (for prototyping)

ORM: SQLAlchemy

Authentication: Flask-Login

Forms: Flask-WTF, WTForms

Password Hashing: Werkzeug.security (using bcrypt)

Database Migrations: Flask-Migrate

Frontend: HTML, CSS, JavaScript

Project Structure
PixelForgeNexus/
├── app.py                     # Main Flask application file
├── config.py                  # Configuration settings (SECRET_KEY, DB URI, etc.)
├── models.py                  # SQLAlchemy database models (User, Project, Document)
├── forms.py                   # WTForms for form validation
├── extensions.py              # Initializes Flask extensions (db, migrate, login_manager) to prevent circular imports
├── utils.py                   # Placeholder for utility functions (currently minimal)
├── templates/                 # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── project_details.html
│   ├── add_project.html
│   ├── assign_team.html
│   ├── upload_document.html
│   ├── account_settings.html
│   ├── users.html
│   └── edit_user_role.html
├── static/                    # Static assets (CSS, JS)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── instance/                  # Instance-specific data (e.g., SQLite database, uploaded files)
│   ├── site.db                # SQLite database file (created on first run)
│   └── uploads/               # Directory for uploaded project documents
└── migrations/                # Flask-Migrate directory for database schema changes

Setup and Installation
Prerequisites
Python 3.x: Ensure Python 3 is installed on your system.

pip: Python's package installer, usually comes with Python.

Git: For cloning the repository (if you're not downloading the zip).

Installation Steps
Clone the Repository (or download and extract the zip):

git clone https://github.com/YOUR_GITHUB_USERNAME/PixelForgeNexus.git
cd PixelForgeNexus

(Replace YOUR_GITHUB_USERNAME with your actual GitHub username)

Create a Virtual Environment (Recommended):

python3 -m venv venv

Activate the Virtual Environment:

On Windows:

.\venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

(Your terminal prompt should now show (venv) indicating the environment is active.)

Install Dependencies:

pip install Flask Flask-SQLAlchemy Flask-WTF Flask-Login python-dotenv Flask-Migrate Werkzeug email_validator

Database Setup (First Time)
Ensure Virtual Environment is Activated.

Delete any existing instance/ and migrations/ folders from previous attempts to ensure a clean slate.

# From the PixelForgeNexus directory
rmdir /s /q instance  # On Windows
rmdir /s /q migrations # On Windows
# Or for macOS/Linux:
rm -rf instance
rm -rf migrations

Initialize and Upgrade the Database:

flask db init
flask db migrate -m "Initial database setup"
flask db upgrade

You should see messages indicating the creation of the migration repository and database tables.

How to Run the Application
Ensure your virtual environment is active.

Set the FLASK_APP environment variable:

On Windows:

set FLASK_APP=app.py

On macOS/Linux:

export FLASK_APP=app.py

Start the Flask Development Server:

python app.py

You should see output similar to:

* Serving Flask app 'app'
* Debug mode: on
...
Default admin user created: username='admin', password='Admin@123'
* Running on http://127.0.0.1:5000
Press CTRL+C to quit

Crucially, confirm you see the "Default admin user created" message.

Access the Application:
Open your web browser and navigate to: http://127.0.0.1:5000/

Login Credentials
Upon the first successful run (after a clean database setup), a default administrator user will be created:

Username: admin

Password: Admin@123

Important: For a real-world application, this default password should be changed immediately, and the SECRET_KEY in config.py should be set to a strong, randomly generated value and loaded from an environment variable.

To Create Other Users (Project Leads, Developers):
Log in as admin.

Navigate to the "Manage Users" page (via the dashboard or direct link).

Click "Register New User" and fill in the details, selecting the desired role.

Note: Passwords for new users must meet the strong password requirements (at least 8 characters, with digits, uppercase, lowercase, and special characters).

Security Considerations
PixelForge Nexus is designed with several security principles in mind:

Role-Based Access Control (RBAC): Granular permissions are enforced at the application level using Flask-Login and custom role checks.

Password Hashing: All user passwords are securely hashed and salted using bcrypt (via Werkzeug.security) before storage.

Input Validation: Forms use WTForms validators to ensure data integrity and prevent common injection attacks.

SQL Injection Prevention: SQLAlchemy ORM is used for all database interactions, which automatically parametrizes queries, preventing SQL injection.

XSS Prevention: Jinja2 templating automatically escapes output, mitigating Cross-Site Scripting vulnerabilities.

Secure Session Management: Flask-Login handles user sessions securely.

File Upload Security: werkzeug.utils.secure_filename is used to sanitize uploaded filenames.

Future Enhancements
Multi-Factor Authentication (MFA): Implement a full MFA solution (e.g., TOTP with pyotp) to significantly boost login security.

Email Verification: Add email verification for new user registrations.

Password Reset Functionality: Implement a secure password reset mechanism.

Document Version Control: Add versioning for uploaded documents.

Enhanced Logging & Monitoring: Implement more comprehensive logging for security events and potential anomalies.

File Type Validation: More rigorous validation of uploaded file types beyond just filename sanitization.

Production Deployment: Transition to a production-ready WSGI server (e.g., Gunicorn, uWSGI) and a reverse proxy (e.g., Nginx) with HTTPS enabled.

Cloud Storage for Documents: Integrate with cloud storage solutions (e.g., AWS S3, Google Cloud Storage) for scalable and secure document storage.

This README provides a comprehensive overview of the PixelForge Nexus project.
