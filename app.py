import os

from flask import Flask
from google.cloud import secretmanager


def create_app(test_config=None):
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

    #if test_config is None:
        # Load the instance config, if it exists, when not testing
    #    app.config.from_pyfile('config.py', silent=True)
    #else:
        # Load the test config if passed in
    #    app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    #try:
    #    os.makedirs(app.instance_path)
    #except OSError:
    #    pass

    # A simple page that says hello
    #@app.route('/')
    #def hello():
    #    return 'Hello, World!'

    import auth
    app.register_blueprint(auth.bp)

    import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
