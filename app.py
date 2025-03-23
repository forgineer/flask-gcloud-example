import db
import firebase_admin
import os

from firebase_admin import credentials
from flask import Flask
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound


def create_app():
    """
    Standard app factory. Stands up the application.

    :return: A Flask app instance
    """
    # Initialize the Firebase admin
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

    # Create and configure the app
    app = Flask(__name__)

    # Retrieve project ID
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

    # Retrieve and set the App Secret Key
    try:
        secrets_client = secretmanager.SecretManagerServiceClient()
        secret_name = 'APP_SECRET_KEY'
        secret_version = f'projects/{project_id}/secrets/{secret_name}/versions/latest'

        secret_data = secrets_client.access_secret_version(name=secret_version)
        APP_SECRET_KEY = secret_data.payload.data.decode('UTF-8')

        # Set App config
        app.config.from_mapping(
            SECRET_KEY=APP_SECRET_KEY
        )
    except NotFound:
        raise Exception('Secret APP_SECRET_KEY not found.')
    except Exception as e: # All other exceptions
        raise Exception(e)

    # Import App blueprints
    import auth
    app.register_blueprint(auth.bp)

    import blog
    app.register_blueprint(blog.bp)

    # Set default endpoint (index)
    app.add_url_rule('/', endpoint='index')

    # Define actions after App context ends
    @app.teardown_appcontext
    def teardown(exception):
        db.close_db()

    return app
