# C:\Users\LENOVO\OneDrive\Desktop\pixelforge_nexus\app.py

from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, abort
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# --- 1. Import extensions (db, migrate, login_manager) from extensions.py ---
# This breaks the circular import dependency
from extensions import db, migrate, login_manager

# --- 2. Import Flask-Login components needed directly in app.py's routes ---
# Ensure ALL necessary components are imported here, including login_required, current_user, etc.
from flask_login import login_required, current_user, login_user, logout_user

# --- 3. Import Models (now safe to import after extensions are defined) ---
from models import User, Project, Document, project_assignments

# --- 4. Import Forms (Forms often depend on Models, so import after them) ---
from forms import LoginForm, RegistrationForm, AddProjectForm, AssignTeamForm, UploadDocumentForm, UpdatePasswordForm, UserManagementForm


# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- Initialize extensions and bind them to the app instance ---
# This must happen AFTER app is created and BEFORE routes are defined
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirect to login page if user is not logged in


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user_loader callback.
    Loads a user from the database given their ID.
    """
    return User.query.get(int(user_id))

# --- Context Processors ---
@app.context_processor
def inject_user_roles():
    """
    Injects user role flags (is_admin, is_project_lead, is_developer)
    into all templates for conditional rendering based on user role.
    """
    if current_user.is_authenticated:
        return {
            'is_admin': current_user.is_admin(),
            'is_project_lead': current_user.is_project_lead(),
            'is_developer': current_user.is_developer()
        }
    return {'is_admin': False, 'is_project_lead': False, 'is_developer': False}

# --- Routes ---

@app.route('/')
@app.route('/index')
@login_required # This decorator requires 'login_required' to be imported
def index():
    if current_user.is_admin():
        projects = Project.query.all()
    elif current_user.is_project_lead():
        projects = Project.query.filter_by(lead_id=current_user.id).all()
    else: # Developer
        projects = current_user.assigned_projects.all()
    return render_template('index.html', title='Dashboard', projects=projects)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        flash(f'Welcome, {user.username}!', 'success')
        return redirect(next_page) if next_page else redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """
    Admin-only route for registering new users.
    """
    if not current_user.is_admin():
        flash('You do not have permission to register new users.', 'danger')
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.username} has been registered successfully as {user.role}.', 'success')
        return redirect(url_for('users')) # Redirect to user management page
    return render_template('register.html', title='Register New User', form=form)

@app.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    """
    Allows authenticated users to update their password.
    MFA setup is a placeholder in the template.
    """
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Incorrect current password.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('account_settings'))
    return render_template('account_settings.html', title='Account Settings', form=form)

@app.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    """
    Admin-only route to add new game projects.
    Ensures a Project Lead exists before allowing project creation.
    """
    if not current_user.is_admin():
        flash('You do not have permission to add projects.', 'danger')
        return redirect(url_for('index'))

    # Pre-check for available project leads before rendering the form
    project_leads_exist = User.query.filter_by(role='project_lead').first()
    if not project_leads_exist:
        flash('No Project Leads are registered. Please register a Project Lead before adding a project.', 'warning')
        return redirect(url_for('users')) # Redirect to user management to register a lead

    form = AddProjectForm()
    if form.validate_on_submit():
        # Ensure the selected lead_id corresponds to a project_lead role
        project_lead_user = User.query.get(form.lead_id.data)
        if not project_lead_user or not project_lead_user.is_project_lead():
            flash('Invalid Project Lead selected. Please select a user with the "Project Lead" role.', 'danger')
            return render_template('add_project.html', title='Add Project', form=form)

        project = Project(
            name=form.name.data,
            description=form.description.data,
            deadline=form.deadline.data,
            lead_id=form.lead_id.data
        )
        db.session.add(project)
        db.session.commit()
        flash(f'Project "{project.name}" added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_project.html', title='Add Project', form=form)

@app.route('/project/<int:project_id>')
@login_required
def project_details(project_id):
    """
    Displays details of a specific project.
    Access controlled: Only assigned users, project leads, or admins can view.
    """
    project = Project.query.get_or_404(project_id)

    # Access control logic
    if not current_user.is_admin() and \
       not (current_user.is_project_lead() and current_user.id == project.lead_id) and \
       not (current_user.is_developer() and current_user in project.assigned_developers.all()):
        flash('You do not have permission to view this project.', 'danger')
        return redirect(url_for('index'))

    return render_template('project_details.html', title=project.name, project=project)

@app.route('/project/<int:project_id>/mark_completed')
@login_required
def mark_project_completed(project_id):
    """
    Admin-only route to mark a project as completed.
    """
    if not current_user.is_admin():
        flash('You do not have permission to mark projects as completed.', 'danger')
        return redirect(url_for('index'))

    project = Project.query.get_or_404(project_id)
    project.is_completed = True
    db.session.commit()
    flash(f'Project "{project.name}" marked as completed!', 'success')
    return redirect(url_for('index'))

@app.route('/project/<int:project_id>/assign_team', methods=['GET', 'POST'])
@login_required
def assign_team(project_id):
    """
    Project Lead (for their projects) or Admin can assign developers to a project.
    """
    project = Project.query.get_or_404(project_id)

    # Access control logic
    if not current_user.is_admin() and not (current_user.is_project_lead() and current_user.id == project.lead_id):
        flash('You do not have permission to assign team members to this project.', 'danger')
        return redirect(url_for('project_details', project_id=project.id))

    form = AssignTeamForm(project_id=project.id)
    if form.validate_on_submit():
        developer = User.query.get(form.developers.data)
        if developer and developer.is_developer() and developer not in project.assigned_developers.all():
            project.assigned_developers.append(developer)
            db.session.commit()
            flash(f'{developer.username} assigned to project "{project.name}".', 'success')
            return redirect(url_for('project_details', project_id=project.id))
        else:
            flash('Invalid developer or already assigned.', 'warning')
    return render_template('assign_team.html', title=f'Assign Team to {project.name}', form=form, project=project)

@app.route('/project/<int:project_id>/upload_document', methods=['GET', 'POST'])
@login_required
def upload_document(project_id):
    """
    Admin or Project Lead (for their projects) can upload documents.
    Handles file saving and database entry for documents.
    """
    project = Project.query.get_or_404(project_id)

    # Access control logic
    if not current_user.is_admin() and not (current_user.is_project_lead() and current_user.id == project.lead_id):
        flash('You do not have permission to upload documents for this project.', 'danger')
        return redirect(url_for('project_details', project_id=project.id))

    form = UploadDocumentForm()
    if form.validate_on_submit():
        if 'document' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['document']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            document = Document(
                filename=filename,
                filepath=filepath,
                project_id=project.id,
                uploaded_by_id=current_user.id
            )
            db.session.add(document)
            db.session.commit()
            flash(f'Document "{filename}" uploaded successfully!', 'success')
            return redirect(url_for('project_details', project_id=project.id))
    return render_template('upload_document.html', title=f'Upload Document for {project.name}', form=form, project=project)


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """
    Serves uploaded files from the UPLOAD_FOLDER.
    Access controlled: Only assigned users, project leads, or admins can view.
    """
    document = Document.query.filter_by(filename=filename).first()
    if not document:
        flash('Document not found.', 'danger')
        abort(404) # Or redirect to a project page

    project = document.project

    # Access control logic
    if not current_user.is_admin() and \
       not (current_user.is_project_lead() and current_user.id == project.lead_id) and \
       not (current_user.is_developer() and current_user in project.assigned_developers.all()):
        flash('You do not have permission to view this document.', 'danger')
        return redirect(url_for('index'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/users')
@login_required
def users():
    """
    Admin-only route to manage all user accounts (view, edit roles, delete).
    """
    if not current_user.is_admin():
        flash('You do not have permission to manage users.', 'danger')
        return redirect(url_for('index'))
    all_users = User.query.all()
    return render_template('users.html', title='Manage Users', users=all_users)

@app.route('/user/<int:user_id>/edit_role', methods=['GET', 'POST'])
@login_required
def edit_user_role(user_id):
    """
    Admin-only route to edit a user's role.
    """
    if not current_user.is_admin():
        flash('You do not have permission to edit user roles.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user) # Populate form with existing user data

    if form.validate_on_submit():
        user.role = form.role.data
        db.session.commit()
        flash(f'Role for user "{user.username}" updated to "{user.role}".', 'success')
        return redirect(url_for('users'))
    return render_template('edit_user_role.html', title=f'Edit Role for {user.username}', form=form, user=user)

@app.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """
    Admin-only route to delete a user.
    Handles disassociating user from projects and deleting their uploaded documents.
    Prevents an admin from deleting their own account.
    """
    if not current_user.is_admin():
        flash('You do not have permission to delete users.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for('users'))

    # Disassociate user from projects they lead
    for project in user.projects_led.all():
        project.lead_id = None # Set lead to None, or reassign if complex logic is needed

    # Remove user from assigned projects (many-to-many relationship)
    for project in user.assigned_projects.all():
        project.assigned_developers.remove(user)

    # Delete documents uploaded by this user (and their physical files)
    for document in user.uploaded_documents.all():
        try:
            os.remove(document.filepath)
        except OSError as e:
            print(f"Error deleting file {document.filepath}: {e}") # Log error but don't stop deletion
        db.session.delete(document)

    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.username}" and associated data deleted.', 'success')
    return redirect(url_for('users'))

if __name__ == '__main__':
    # This block runs only when app.py is executed directly (not imported)
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        # Create an initial admin user if none exists for demonstration purposes
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@pixelforge.com', role='admin')
            admin_user.set_password('Admin@123') # IMPORTANT: CHANGE THIS IN PRODUCTION
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username='admin', password='Admin@123'")
    app.run(debug=True) # debug=True enables auto-reloading and helpful error messages