# C:\Users\LENOVO\OneDrive\Desktop\pixelforge_nexus\extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()