from datetime import datetime
from FlaskWebProject import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from azure.storage.blob import BlockBlobService
import string, random
from werkzeug.utils import secure_filename
from flask import flash

blob_container = app.config['BLOB_CONTAINER']
blob_service = BlockBlobService(
    account_name=app.config['BLOB_ACCOUNT'],
    account_key=app.config['BLOB_STORAGE_KEY']
)

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# -------------------- USER MODEL --------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(150), unique=True)  # MS login
    ms_id = db.Column(db.String(150), unique=True)  # MS login

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# -------------------- POST MODEL --------------------
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    subtitle = db.Column(db.String(255))  # New subtitle field
    author = db.Column(db.String(75))
    body = db.Column(db.String(800))
    image_path = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.title)

    # -------------------- SAVE/UPDATE POST --------------------
    def save_changes(self, form, file=None, userId=None, new=False):
        try:
            self.title = form.title.data or self.title
            self.subtitle = getattr(form, 'subtitle', None) and form.subtitle.data or self.subtitle
            self.author = form.author.data or self.author
            self.body = form.body.data or self.body
            if userId:
                self.user_id = userId

            # Handle image upload safely
            if file and hasattr(file, 'filename') and file.filename != '':
                filename = secure_filename(file.filename)
                fileextension = filename.rsplit('.', 1)[1]
                Randomfilename = id_generator()
                filename = Randomfilename + '.' + fileextension
                try:
                    blob_service.create_blob_from_stream(blob_container, filename, file)
                    # Delete old image if exists
                    if self.image_path:
                        blob_service.delete_blob(blob_container, self.image_path)
                    self.image_path = filename
                except Exception as e:
                    flash(f"Blob upload failed: {str(e)}")

            if new:
                db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to save post: {str(e)}")

    # -------------------- DELETE POST --------------------
    def delete_post(self):
        try:
            if self.image_path:
                blob_service.delete_blob(blob_container, self.image_path)
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to delete post: {str(e)}")

    # -------------------- REMOVE IMAGE --------------------
    def remove_image(self):
        try:
            if self.image_path:
                blob_service.delete_blob(blob_container, self.image_path)
                self.image_path = None
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to remove image: {str(e)}")
