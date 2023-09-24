import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/registrar', methods=('GET', 'POST'))
def registrar(): 
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        db = get_db()
        error = None

        if not usuario:
            error = 'El usuario es requerido'
        elif not clave: 
            error = 'La contraseña es requerida'

        if error is None: 
            try: 
                db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)', 
                    (usuario, generate_password_hash(clave))
                )
                db.commit()
            except db.IntegrityError: 
                error = f'Usuario {usuario} ya está registrado'
            else: 
                return redirect(url_for('auth.login'))
        flash(error)
    
    return render_template('auth/registrar.html')

@bp.route('/iniciar', methods=('GET', 'POST'))
def iniciar(): 
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (usuario)
        ).fetchone()

        if user is None: 
            error = 'Usuario incorrecto'
        elif not check_password_hash(user['password'], clave): 
            error = 'Contraseña incorrecta'

        if error is None: 
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/iniciar.html')

@bp.before_app_request
def cargar_usuaria_iniciado():
    user_id = session.get('user_id')

    if user_id is None: 
        g.user = None
    else: 
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id)
        ).fetchone()

@bp.route('/salir')
def salir(): 
    session.clear()
    return redirect(url_for('index'))

def inicio_requerido(vista): 
    @functools.wraps(vista)
    def wrapped_view(**kwargs): 
        if g.user is None: 
            return redirect(url_for('auth.iniciar'))
        
        return vista(**kwargs)
    
    return wrapped_view

@bp.route('/chao')
def chao():
    return 'chaitos, chaitos, chao, chao'