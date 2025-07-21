import os

from flask import Flask


def create_app():
    """
    Standard app factory. Stands up the application.
    This is a dummy application to deploy to App Engine instead of a real one.

    :return: A Flask app instance
    """
    # Create and configure the app
    dummy = Flask(__name__)

    @dummy.route("/")
    def hello():
        # Retrieve project ID
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        return f'<p>Hello, my name is {project_id}!</p>'

    return dummy


# Entry point for App Engine
app = create_app()
