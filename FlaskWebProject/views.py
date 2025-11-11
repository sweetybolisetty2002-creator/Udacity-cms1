"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, flash, redirect, request, session, url_for
from werkzeug.urls import url_parse
from config import Config
from FlaskWebProject import app, db
from FlaskWebProject.forms import LoginForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from FlaskWebProject.models import User, Post
import msal
import uuid

# ------------------ APP STARTUP ------------------
app.logger.info("✅ Flask application started successfully and is running on Azure.")

imageSourceUrl = 'https://' + app.config['BLOB_ACCOUNT'] + '.blob.core.windows.net/' + app.config['BLOB_CONTAINER'] + '/'

# ------------------ HOME ------------------
@app.route('/')
@app.route('/home')
@login_required
def home():
    posts = Post.query.all()
    app.logger.info(f"User '{current_user.username}' accessed the home page.")
    return render_template(
        'index.html',
        title='Home Page',
        posts=posts,
        imageSource=imageSourceUrl
    )

# ------------------ NEW POST ------------------
@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        file = request.files.get('image_path')
        post = Post()
        post.save_changes(form, file, current_user.id, new=True)
        app.logger.info(f"User '{current_user.username}' created a new post titled '{form.title.data}'.")
        flash('Post created successfully!')
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Create Post',
        imageSource=imageSourceUrl,
        form=form
    )

# ------------------ EDIT POST ------------------
@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        file = request.files.get('image_path')
        post.save_changes(form, file, current_user.id)
        app.logger.info(f"User '{current_user.username}' updated post ID {id} titled '{form.title.data}'.")
        flash('Post updated successfully!')
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Edit Post',
        form=form,
        imageSource=imageSourceUrl
    )

# ------------------ DELETE POST ------------------
@app.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != current_user.id:
        app.logger.warning(f"Unauthorized delete attempt by '{current_user.username}' on post ID {id}.")
        flash('You are not authorized to delete this post.')
        return redirect(url_for('home'))
    post.delete_post()
    app.logger.info(f"User '{current_user.username}' deleted post ID {id}.")
    flash('Post deleted successfully!')
    return redirect(url_for('home'))

# ------------------ REMOVE IMAGE ------------------
@app.route('/post/<int:id>/remove_image', methods=['POST'])
@login_required
def remove_image(id):
    post = Post.query.get_or_404(id)
    if post.user_id != current_user.id:
        app.logger.warning(f"Unauthorized image removal attempt by '{current_user.username}' on post ID {id}.")
        flash('You are not authorized to remove the image.')
        return redirect(url_for('home'))
    post.remove_image()
    app.logger.info(f"User '{current_user.username}' removed image from post ID {id}.")
    flash('Image removed successfully!')
    return redirect(url_for('post', id=id))

# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        app.logger.info(f"User '{current_user.username}' is already logged in.")
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            app.logger.warning(f"Failed login attempt for username: {form.username.data}")
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        app.logger.info(f"User '{user.username}' logged in successfully.")
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)

    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=Config.SCOPE, state=session["state"])
    return render_template('login.html', title='Sign In', form=form, auth_url=auth_url)

# ------------------ MICROSOFT LOGIN REDIRECT ------------------
@app.route(Config.REDIRECT_PATH)
def authorized():
    if request.args.get('state') != session.get("state"):
        app.logger.warning("State mismatch during Microsoft login redirect.")
        return redirect(url_for("home"))

    if "error" in request.args:
        app.logger.error(f"Microsoft login error: {request.args}")
        return render_template("auth_error.html", result=request.args)

    if "code" in request.args:
        cache = _load_cache()
        result = None  # TODO: Implement MSAL token acquisition here
        if not result or "error" in result:
            app.logger.error(f"MSAL token acquisition error: {result}")
            return render_template("auth_error.html", result=result)

        user_claims = result.get("id_token_claims")
        email = user_claims.get("preferred_username")
        ms_id = user_claims.get("oid")

        user = User.query.filter_by(ms_id=ms_id).first()
        if not user:
            user = User(username=email.split('@')[0], email=email, ms_id=ms_id)
            db.session.add(user)
            db.session.commit()
            app.logger.info(f"New Microsoft user '{user.username}' created.")
        login_user(user)
        app.logger.info(f"Microsoft user '{user.username}' logged in successfully.")
        _save_cache(cache)
    return redirect(url_for('home'))

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    app.logger.info(f"User '{current_user.username}' logged out.")
    logout_user()
    session.clear()
    return redirect(
        Config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("login", _external=True)
    )

# ------------------ MSAL UTILS ------------------
def _load_cache():
    # TODO: Load MSAL token cache
    return None

def _save_cache(cache):
    # TODO: Save MSAL token cache
    pass

def _build_msal_app(cache=None, authority=None):
    # TODO: Return a ConfidentialClientApplication
    return None

def _build_auth_url(authority=None, scopes=None, state=None):
    # TODO: Return MSAL auth request URL
    return None
