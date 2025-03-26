# Notes
Enable Firebase Authentication
Enable Firestore
Enable Secrets Manager
Install SDK (CLI)

Packages:
```commandline
flask
google-cloud-secret-manager
google-cloud-firestore
firebase-admin
gunicorn
```


Accepts credentials that are used to authenticate to and authorize access to Google Cloud services.
```commandline
gcloud auth login

```

Generates a local ADC file based on the credentials you provide to the command.
```commandline
gcloud auth application-default login
```

