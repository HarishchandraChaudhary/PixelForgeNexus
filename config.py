# C:\Users\LENOVO\OneDrive\Desktop\pixelforge_nexus\config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_super_secret_key_here_replace_in_prod'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'instance/uploads' # Where documents will be stored
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload size