from flask import g
from google.cloud import firestore


def get_db():
    if 'db' not in g:
        g.db = firestore.Client()

    return g.db


def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()
