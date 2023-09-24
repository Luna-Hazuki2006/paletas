from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from auth import inicio_requerido
from db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index(): 
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/crear', methods=('GET', 'POST'))
@inicio_requerido
def crear():
    if request.method == 'POST':
        titulo = request.form['titulo']
        cuerpo = request.form['cuerpo']
        error = None

        if not titulo:
            error = 'El título es necesario'
        if error is not None: 
            flash(error)
        else: 
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (titulo, cuerpo, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/crear.html')

def get_post(id, check_author=True): 
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id)
    ).fetchone()

    if post is None: 
        abort(404, f'La id {id} del post no existe')
    
    if check_author and post['author_id'] != g.user['id']: 
        abort(403)
    
    return post

@bp.route('/<int:id>/modificar', methods=('GET', 'POST'))
@inicio_requerido
def modificar(id): 
    post = get_post(id)

    if request.method == 'POST': 
        titulo = request.form['titulo']
        cuerpo = request.form['cuerpo']
        error = None

        if not titulo: 
            error = 'El título es necesario'

        if error is not None: 
            flash(error)
        else: 
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (titulo, cuerpo, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/modificar.html', post=post)

@bp.route('/<int:id>/borrar', methods=('POST'))
@inicio_requerido
def borrar(id): 
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id))
    db.commit()
    return redirect(url_for('blog.index'))