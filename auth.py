import functools

from db import get_db
from firebase_admin import auth
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from google.cloud.firestore import (
    CollectionReference, DocumentSnapshot, FieldFilter
)
from google.cloud.firestore_v1.stream_generator import StreamGenerator


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    """
    # TODO: Completed this!

    :return:
    """
    uid: str | None = session.get('uid', None)
    username: str | None = session.get('username', None)

    if uid is None:
        g.user = None
    else:
        g.user = {
            'uid': uid
            , 'username': username
        }


def login_required(view):
    """
    # TODO: Complete this!

    :param view:
    :return:
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    # TODO: Complete this!

    :return:
    """
    if request.method == 'POST':
        # Unpack Form Inputs
        email: str = request.form['email']
        username: str = request.form['username']
        password: str = request.form['password']
        db = get_db() # Firebase client
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
            records: StreamGenerator[DocumentSnapshot] = users_ref.where(
                filter=FieldFilter("username", "==", username)
            ).limit(1).stream()

            for record in records:
                user_record: dict = record.to_dict()
                record_username: str | None = user_record.get('username', None)

                if record_username == username:
                    error = f'User {username} is already registered.'

        # Register the new user and create a record
        if error is None:
            try:
                # New Firebase Authentication User
                new_user: auth.UserRecord = auth.create_user(
                    email=email
                    , password=password
                    , display_name=username
                )

                # New Firestore User Record
                new_user_record = {
                    'uid': new_user.uid
                    , 'username': new_user.display_name
                    , 'email': new_user.email
                }

                db.collection('users').document().set(new_user_record)

                return redirect(url_for("blog.posts"))
            except Exception as e:
                error = e

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    # TODO: Completed this!

    :return:
    """
    if request.method == 'POST':
        id_token: str = request.form.get('idToken', '')
        error: str =  request.form.get('error', '')

        if id_token: # Firebase authentication token returned
            try:
                decoded_token = auth.verify_id_token(id_token)
                uid = decoded_token['uid']  # Verified UID?

                # Check Firestore for user
                # Query the Firestore for a user with the username
                db = get_db() # Firebase client
                users_ref: CollectionReference = db.collection('users')
                records: StreamGenerator[DocumentSnapshot] = users_ref.where(
                    filter=FieldFilter("uid", "==", uid)
                ).limit(1).stream()

                for record in records:
                    user_record: dict = record.to_dict()
                    username: str = user_record.get('username')

                    # Clear and set session cookie
                    # Return to blog post
                    session.clear()
                    session['uid'] = uid
                    session['username'] = username

                    return redirect(url_for('blog.posts'))
                else:
                    error = 'User not found in Firestore.'
            except Exception as e:
                error = e
        elif error: # Firebase authentication error caught
            pass
        else: # No token. What happun?
            error = "No token provided."

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout() -> Response:
    """
    Clear the current session cookie of all contents.

    :return: Response
    """
    session.clear()

    return redirect(url_for('blog.posts'))
