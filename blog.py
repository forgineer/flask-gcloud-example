import db

from auth import login_required
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from google.cloud import firestore
from werkzeug.exceptions import abort


bp = Blueprint('blog', __name__)


def get_blog_posts(limit=100):
    """
    Get blog posts from Firestore. Created for simplification of sharing between
    index and posts endpoints.

    :param limit: A number used to define the Firestore query limit.
    :return: A list object with all blog posts data.
    """
    # Retrieve the records (blog posts) from Firestore
    firestoredb = db.get_db()
    records = firestoredb.collection('posts').limit(limit).stream()

    # Return posts as records (with document ID)
    _posts = []

    for record in records:
        post = record.to_dict()
        post['id'] = record.id
        _posts.append(post)

    return _posts


@bp.route('/')
def index():
    """
    Endpoint for the app landing page.

    :return: Blog posts view with posts data.
    """
    posts = get_blog_posts()
    return render_template('blog/index.html', posts=posts)


@bp.route('/posts')
def posts():
    """
    Endpoint for the blog posts view.

    :return: Blog posts view with posts data.
    """
    posts = get_blog_posts()
    return render_template('blog/posts.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """
    Creates a new blog post.

    :return: If successful create, return to blog posts view. Else, return to create view.
    """
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            try:
                # Build the document
                data = {
                    'title': title
                    , 'body': body
                    , 'username': session.get('username')
                    , 'author_id': session.get('uid')
                    , 'created': firestore.SERVER_TIMESTAMP
                    , 'updated': firestore.SERVER_TIMESTAMP
                }

                # Store the document
                firestoredb = db.get_db()
                firestoredb.collection('posts').add(data)

                return redirect(url_for('blog.posts'))
            except Exception as e:
                error = e

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    """
    Retrieves a singular document/post from Firestore.

    :param id: The unique ID of the document/post.
    :param check_author: Verifies the author is the current user.
    :return: If found, the post. Else, abort.
    """
    firestoredb = db.get_db()
    doc = firestoredb.collection('posts').document(id).get()

    if doc.exists:
        post = doc.to_dict()
        post['id'] = doc.id

        if check_author and post['author_id'] != g.user['uid']:
            abort(403)

        return post
    else:
        abort(404, f"Post id {id} doesn't exist.")


@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """
    Updates an existing blog post.

    :param id: The unique ID of the document/post.
    :return: If successful update, return to blog posts view. Else, return to update view.
    """
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            try:
                data = {
                    'title': title
                    , 'body': body
                    , 'updated': firestore.SERVER_TIMESTAMP
                }

                firestoredb = db.get_db()
                update_ref = firestoredb.collection('posts').document(id).update(data)

                return redirect(url_for('blog.posts'))
            except Exception as e:
                flash(e)

    return render_template('blog/update.html', post=post)


@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """
    Deletes an existing blog post.

    :param id: The unique ID of the document/post.
    :return: If successful delete, return to blog posts view. Else, return to update view.
    """
    try:
        firestoredb = db.get_db()
        delete_ref = firestoredb.collection('posts').document(id).delete()
    except Exception as e:
        flash(e)

    return redirect(url_for('blog.posts'))
