import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

    # Azure Blob Storage configuration
    BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT', 'image11')
    BLOB_STORAGE_KEY = os.environ.get('BLOB_STORAGE_KEY', 'STORAGE_KEY_NAME')
    BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER', 'images')

    # SQL Server configuration
    SQL_SERVER = os.environ.get('SQL_SERVER', 'ENTER_SQL_SERVER_NAME.database.windows.net')
    SQL_DATABASE = os.environ.get('SQL_DATABASE', 'ENTER_SQL_DB_NAME')
    SQL_USER_NAME = os.environ.get('SQL_USER_NAME', 'ENTER_SQL_SERVER_USERNAME')
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD', 'ENTER_SQL_SERVER_PASSWORD')

    # Fixed SQLAlchemy connection string formatting
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{SQL_USER_NAME}:{SQL_PASSWORD}@{SQL_SERVER}:1433/{SQL_DATABASE}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Microsoft Authentication (Azure AD) configuration
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET', 'ENTER_CLIENT_SECRET_HERE')
    CLIENT_ID = os.environ.get('CLIENT_ID', 'ENTER_CLIENT_ID_HERE')
    AUTHORITY = "https://login.microsoftonline.com/common"  # Multi-tenant, or replace with tenant ID
    REDIRECT_PATH = "/getAToken"
    SCOPE = ["User.Read"]  # Permissions for Microsoft Graph API

    # Session configuration
    SESSION_TYPE = "filesystem"
