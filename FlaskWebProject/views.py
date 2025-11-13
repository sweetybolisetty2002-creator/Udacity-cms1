from datetime import datetime
from flask import render_template, flash, redirect, request, session, url_for
from urllib.parse import urlparse
from config import Config
from FlaskWebProject import app, db
from FlaskWebProject.forms import LoginForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from FlaskWebProject.models import User, Post
import msal
import uuid
from azure.storage.blob import BlockBlobService
from werkzeug.utils import secure_filename
import os

# ------------------ APP STARTUP ------------------
app.logger.info("✅ Flask application started successfully and is running on Azure.")

# Azure Blob storage service
blob_service = BlockBlobService(
    account_name=app.config['BLOB_ACCOUNT'],
    account_key=app.config['BLOB_STORAGE_KEY']
)
imageSourceUrl = f'https://{app.config["BLOB_ACCOUNT"]}.blob.core.windows.net/{app.config["BLOB_CONTAINER"]}/'

# ------------------ HOME ------------------
@app.route('/')
@app.route('/home')
@login_required
def home():
    posts = Post.query.all()
    return render_template('index.html', title='Home Page', posts=posts, imageSource=imageSourceUrl)

# ------------------ UPLOAD IMAGE ------------------
@app.route('/post/<int:post_id>/upload_image', methods=['POST'])
@login_required
def upload_image(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You are not authorized to upload image for this post.')
        return redirect(url_for('home'))

    file = request.files.get('file')
    if file:
        filename = secure_filename(file.filename)
        try:
            # Upload directly to Azure Blob Storage
            blob_service.create_blob_from_stream(
                container_name=app.config['BLOB_CONTAINER'],
                blob_name=filename,
                stream=file
            )
            # Save the filename in the database
            post.image_path = filename
            db.session.commit()
            flash('Image uploaded successfully!')
        except Exception as e:
            app.logger.error(f"Azure Blob upload failed: {str(e)}")
            flash('Failed to upload image. Check logs.')
    return redirect(url_for('home'))

# ------------------ NEW POST ------------------
@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.save_changes(form, None, current_user.id, new=True)
        flash('Post created successfully!')
        return redirect(url_for('home'))
    return render_template('post.html', title='Create Post', imageSource=imageSourceUrl, form=form)

# ------------------ EDIT POST ------------------
@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    form = PostForm(formdata=request.form, obj=post)
    if form.validate_on_submit():
        post.save_changes(form, None, current_user.id)
        flash('Post updated successfully!')
        return redirect(url_for('home'))
    return render_template('post.html', title='Edit Post', form=form, imageSource=imageSourceUrl)

# ------------------ DELETE POST ------------------
@app.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != current_user.id:
        flash('You are not authorized to delete this post.')
        return redirect(url_for('home'))
    post.delete_post()
    flash('Post deleted successfully!')
    return redirect(url_for('home'))

# ------------------ REMOVE IMAGE ------------------
@app.route('/post/<int:id>/remove_image', methods=['POST'])
@login_required
def remove_image(id):
    post = Post.query.get_or_404(id)
    if post.user_id != current_user.id:
        flash('You are not authorized to remove the image.')
        return redirect(url_for('home'))
    if post.image_path:
        try:
            blob_service.delete_blob(app.config['BLOB_CONTAINER'], post.image_path)
        except Exception as e:
            app.logger.error(f"Failed to delete blob: {str(e)}")
        post.image_path = None
        db.session.commit()
        flash('Image removed successfully!')
    return redirect(url_for('post', id=id))
