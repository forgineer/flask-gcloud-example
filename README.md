# flask-gcloud-example

A proof-of-concept project demonstrating a Flask web application deployed on Google App Engine. This application is an adaptation of the official Flask Blog tutorial, enhanced with modern technologies like Google Firebase for authentication, Firestore for the database, and HTMX for improved user interface reactivity.

## Features

* User authentication (registration and login) via Google Firebase Authentication.
* Create, Read, Update, and Delete (CRUD) operations for blog posts.
* Blog posts stored in Google Firestore.
* Reactive UI elements powered by HTMX for a smoother user experience.
* Ready for deployment to Google App Engine.

## Technologies Used

* **Backend:** Flask, Gunicorn
* **Frontend:** HTMX, CSS
* **Google Cloud Platform:**
  * App Engine
  * Firebase Authentication
  * Firestore
  * Secret Manager

## Prerequisites

* Python 3.11 (Note: Google Cloud Platform supports more recent versions of Python if desired.)
* [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install) installed.
* A Google Cloud Project with the following APIs enabled:
  * Firebase Authentication
  * Firestore
  * Secret Manager

## Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/forgineer/flask-gcloud-example.git
    cd flask-gcloud-example
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    pip install -r requirements.txt
    ```

3.  **Authenticate with Google Cloud:**
    
    Log in with your user credentials. This is used for managing GCP resources.
    ```bash
    gcloud auth login
    ```
    
    Create Application Default Credentials (ADC) for local development. The application will use these credentials to authenticate with Google Cloud services.
    ```bash
    gcloud auth application-default login
    ```

4.  **Run the application:**
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Deployment to Google App Engine

This application is configured for deployment to the Google App Engine standard environment via the `app.yaml` file.

1.  **Set your Google Cloud Project ID:**
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```

2.  **Deploy the application:**
    ```bash
    gcloud app deploy
    ```
    
    Follow the prompts to select a region and confirm the deployment. Once deployed, the command will output the URL to your live application.

### A Note on Firebase API Keys

You might notice that the Firebase configuration in `templates/firebase.js`, including the `apiKey`, is publicly visible. This is by design and is considered a safe practice.

*   **Identification, Not Authorization:** The `apiKey` is used to identify your Firebase project on Google's servers, not to grant access to your data. It is a public identifier, not a secret credential.
*   **Security is Handled by Rules:** The security of your application's data is enforced by Firebase Security Rules for services like Firestore. These rules, defined on the backend, control who can read, write, and modify data.

For more information, you can refer to the following resources:

*   **Stack Overflow:** [Is it safe to expose Firebase API key to the public?](https://stackoverflow.com/questions/37482366/is-it-safe-to-expose-firebase-api-key-to-the-public)
*   **Firebase Documentation:** [Understand Firebase projects](https://firebase.google.com/docs/projects/learn-more#api-keys)

**Important:** If you are using this project as a template, you must replace the Firebase configuration in `templates/firebase.js` with the keys from your own Firebase project.

## Dummy Application

The `dummy.py` module contains a simple Flask application that can be deployed to Google App Engine in place of the main blog application. This is a security measure to avoid exposing the fully functional blog application, which could be vulnerable to malicious attacks such as brute-force creation of blog posts.

The dummy app serves as a "Hello, World!" example and can be safely deployed for testing or demonstration purposes.

### Deploying the Dummy Application

To deploy the dummy application, you need to modify the `entrypoint` in the `app.yaml` file.

1.  **Open `app.yaml`:**
    Change the `entrypoint` from:
    ```yaml
    entrypoint: gunicorn -b :$PORT app:blog
    ```
    to:
    ```yaml
    entrypoint: gunicorn -b :$PORT dummy:app
    ```

2.  **Deploy to App Engine:**
    Follow the regular deployment steps:
    ```bash
    gcloud app deploy
    ```