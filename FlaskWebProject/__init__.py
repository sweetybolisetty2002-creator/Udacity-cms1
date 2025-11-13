"""
The flask application package.
"""
import logging
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
import os

app = Flask(__name__)
app.config.from_object(Config)
# TODO: Add any logging levels and handlers with app.logger
if not os.path.exists('logs'):
    os.mkdir('logs')

# Configure the app logger
logging.basicConfig(
    level=logging.INFO,  # You can change to DEBUG for more details
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()  # This makes logs visible in Azure Log Stream
    ]
)

app.logger.info("Flask application has started.")


Session(app)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

import FlaskWebProject.views
