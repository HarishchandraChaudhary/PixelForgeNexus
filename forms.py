# C:\Users\LENOVO\OneDrive\Desktop\pixelforge_nexus\forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User, Project # Ensure these are imported from models

import re

# Custom validator for strong passwords
def strong_password(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), strong_password])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('project_lead', 'Project Lead'), ('developer', 'Developer')], validators=[DataRequired()])
    submit = SubmitField('Register User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AddProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(min=2, max=128)])
    description = TextAreaField('Description')
    deadline = DateField('Deadline (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    lead_id = SelectField('Project Lead', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Project')

    def __init__(self, *args, **kwargs):
        super(AddProjectForm, self).__init__(*args, **kwargs)
        project_leads = User.query.filter_by(role='project_lead').all()
        if project_leads:
            self.lead_id.choices = [(user.id, user.username) for user in project_leads]
        else:
            self.lead_id.choices = [(0, 'No Project Leads Available')]


class AssignTeamForm(FlaskForm):
    developers = SelectField('Developers', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Developer')

    def __init__(self, project_id=None, *args, **kwargs):
        super(AssignTeamForm, self).__init__(*args, **kwargs)
        self.developers.choices = []
        if project_id:
            project = Project.query.get(project_id)
            if project:
                assigned_dev_ids = [dev.id for dev in project.assigned_developers]
                available_developers = User.query.filter_by(role='developer').filter(User.id.notin_(assigned_dev_ids)).all()
                if available_developers:
                    self.developers.choices = [(user.id, user.username) for user in available_developers]
                else:
                    self.developers.choices = [(0, 'No Developers Available')]


class UploadDocumentForm(FlaskForm):
    submit = SubmitField('Upload Document')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), strong_password])
    new_password2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

class UserManagementForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True})
    role = SelectField('Role', choices=[('admin', 'Admin'), ('project_lead', 'Project Lead'), ('developer', 'Developer')], validators=[DataRequired()])
    submit = SubmitField('Update User Role')