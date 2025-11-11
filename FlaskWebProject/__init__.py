"""
The Flask application package.
"""
import logging
import sys
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_session import Session

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Set up server-side session
Session(app)

# Set up database
db = SQLAlchemy(app)

# Set up login manager
login = LoginManager(app)
login.login_view = 'login'
login.session_protection = "strong"  # optional, adds extra session security

# Make current_user available in all templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Optional: configure logging (Azure Log Stream compatible)
if not app.debug:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("✅ Flask application started and logging to Azure Log Stream.")

# Import views at the end to avoid circular imports
import FlaskWebProject.views
