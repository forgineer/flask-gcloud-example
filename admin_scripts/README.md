# Admin Scripts

This directory contains administrative scripts for managing the application's data. Since this simple blog application does not include an admin console, these scripts provide a way to perform queries, one-off updates, and other administrative tasks directly against the database.

## Notebooks

For simplicity and ease of use, administrative tasks are implemented as Jupyter notebooks. This allows for a more interactive and exploratory approach to data management.

### `users.ipynb`

This notebook contains scripts for querying user information from Firebase Authentication and Firestore. It can be used to reconcile user data between the two services or to perform other user-related administrative tasks.