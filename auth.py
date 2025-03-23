import db
import functools

from firebase_admin import auth
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from google.cloud import firestore


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    """
    Capture the logged-in user from the session cookie before each request.

    :return: None. The logged-in user is loaded into the g.user global.
    """
    uid = session.get('uid', None)
    username = session.get('username', None)

    if uid is None:
        g.user = None
    else:
        g.user = {
            'uid': uid
            , 'username': username
        }


def login_required(view):
    """
    A decorator for wrapping requests that require login access.

    :param view: The request or view being wrapped.
    :return: The wrapped view if the user is logged in. Else, the login view.
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
    Registration of new users into Firebase and Firestore database.

    :return: If registration completes, back to the Blog Posts screen. Else, the login view.
    """
    if request.method == 'POST':
        # Unpack Form Inputs
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        firestoredb = db.get_db() # Firebase client
        error = None

        # Validate Form Input
        if not email:
            error = 'Email is required.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # Verify if the user (email) already exists
        user = None

        if error is None:
            try:
                # Is the user's email already registered?
                user = auth.get_user_by_email(email)
                error = f"Email {email} is already registered."
            except auth.UserNotFoundError:
                pass # In this scenario, unregistered users are acceptable.
            except Exception as e:
                error = e

        # Verify if the username is already being used
        if error is None:
            # Query the Firestore for a user with the username
            users_ref = firestoredb.collection('users')
            records = users_ref.where(
                filter=firestore.FieldFilter("username", "==", username)
            ).limit(1).stream()

            for record in records:
                user_record = record.to_dict()
                record_username = user_record.get('username', None)

                if record_username == username:
                    error = f'User {username} is already registered.'

        # Register the new user and create a record
        if error is None:
            try:
                # New Firebase Authentication User
                new_user = auth.create_user(
                    email=email
                    , password=password
                    , display_name=username
                )

                # New Firestore User Record
                new_user_record = {
                    'uid': new_user.uid
                    , 'username': new_user.display_name
                    , 'email': new_user.email
                    , 'created': firestore.SERVER_TIMESTAMP
                }

                firestoredb.collection('users').document().set(new_user_record)

                return redirect(url_for("blog.posts"))
            except auth.EmailAlreadyExistsError:
                error = f'Email {email} is already registered.'
            except Exception as e:
                error = e

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    User login. Authenticates the user against Firebase and Firestore database as a valid user.

    :return: If login completes, back to the Blog Posts screen as user. Else, the login view.
    """
    if request.method == 'POST':
        id_token = request.form.get('idToken', '')
        error =  request.form.get('error', '')

        if id_token: # Firebase authentication token returned
            try:
                decoded_token = auth.verify_id_token(id_token)
                uid = decoded_token['uid']  # Verified UID?

                # Check Firestore for user
                # Query the Firestore for a user with the username
                firestoredb = db.get_db() # Firebase client
                users_ref = firestoredb.collection('users')
                records = users_ref.where(
                    filter=firestore.FieldFilter("uid", "==", uid)
                ).limit(1).stream()

                for record in records:
                    user_record = record.to_dict()
                    username = user_record.get('username')

                    # Clear and set session cookie
                    # Return to blog post
                    session.clear()
                    session['uid'] = uid
                    session['username'] = username

                    return redirect(url_for('blog.posts'))

                # No records, no user :(
                error = 'User not found in Firestore.'
            except Exception as e:
                error = e
        elif error: # Firebase authentication error caught
            pass # Allow this error to passthrough back to the login view.
        else: # No token. What happun? Edge case.
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
