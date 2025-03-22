from flask import g
from google.cloud import firestore


def get_db():
    """
    Create an instance of the Firestore client class.

    :return: None.
    """
    if 'db' not in g:
        g.db = firestore.Client()

    return g.db


def close_db(e=None):
    """
    Closes the Firestore client at the end of each request.

    :return: None.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()
