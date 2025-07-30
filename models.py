# C:\Users\LENOVO\OneDrive\Desktop\pixelforge_nexus\models.py

from extensions import db # IMPORTANT: Import db from extensions.py, NOT app.py
from flask_login import UserMixin # Ensure UserMixin is explicitly imported
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Association table for Project and User (many-to-many relationship for assigned developers)
project_assignments = db.Table('project_assignments',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin): # UserMixin is correctly added here for Flask-Login
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='developer') # 'admin', 'project_lead', 'developer'

    # Relationships
    projects_led = db.relationship('Project', backref='lead', lazy='dynamic', foreign_keys='Project.lead_id')
    assigned_projects = db.relationship('Project', secondary=project_assignments, backref=db.backref('assigned_developers', lazy='dynamic'))
    uploaded_documents = db.relationship('Document', backref='uploader', lazy='dynamic', foreign_keys='Document.uploaded_by_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_project_lead(self):
        return self.role == 'project_lead'

    def is_developer(self):
        return self.role == 'developer'

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    documents = db.relationship('Document', backref='project', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.name}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    filepath = db.Column(db.String(512), nullable=False) # Path on the server
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Document {self.filename}>'