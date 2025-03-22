import firebase_admin
import os

from firebase_admin import credentials
from flask import Flask
from google.cloud import secretmanager


def create_app(test_config=None):
    # Initialize the Firebase admin
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

    # Create and configure the app
    app = Flask(__name__)

    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

    print(f'project_id: {project_id}')

    secrets_client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{project_id}/secrets/myfirstsecret/versions/latest"

    response = secrets_client.access_secret_version(name=name)
    response_data = response.payload.data.decode('UTF-8')

    print(f'Secret: {response_data}')

    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    import auth
    app.register_blueprint(auth.bp)

    import blog
    app.register_blueprint(blog.bp)

    # Set default endpoint (index)
    app.add_url_rule('/', endpoint='index')

    return app
