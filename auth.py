import functools

from google.cloud.firestore_v1.stream_generator import StreamGenerator

from db import get_db
from firebase_admin import (
    auth, exceptions
)
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from google.cloud.firestore import (
    CollectionReference, DocumentSnapshot, FieldFilter
)
from werkzeug.security import check_password_hash, generate_password_hash


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email: str = request.form['email']
        username: str = request.form['username']
        password: str = request.form['password']
        db = get_db()
        error: str | None = None

        # Validate Form Input
        if not email:
            error = 'Email is required.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # Verify if the user (email) already exists
        user: auth.UserRecord | None = None

        if error is None:
            try:
                # Is the user registered?
                user = auth.get_user_by_email(email)
                error = f"Email {email} is already registered."
            except auth.UserNotFoundError:
                pass
            except Exception as e:
                error = e

        # Verify if the username is already being used
        if error is None:
            # Query the Firestore for a user with the username
            users_ref: CollectionReference = db.collection('users')
            records: StreamGenerator[DocumentSnapshot] = users_ref.where(filter=FieldFilter("username", "==", username)).limit(1).stream()

            for record in records:
                user_record: dict = record.to_dict()
                record_username: str | None = user_record.get('username', None)

                if record_username == username:
                    error = f'User {username} is already registered.'

        # Register the new user and create a record
        if error is None:
            try:
                new_user: auth.UserRecord = auth.create_user(
                    email=email,
                    password=password,
                    display_name=username
                )

                new_user_record = {
                    'username': username
                    , 'email': email
                }

                db.collection('users').document().set(new_user_record)

                return redirect(url_for("blog.posts"))
            except Exception as e:
                error = e

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.posts'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.posts'))
