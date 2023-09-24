import os

from flask import Flask

def crear_app(test_config=None): 
    # crea y configura la aplicación
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='La Reina de la Oscuridad', 
        DATABASE=os.path.join(app.instance_path, 'paletas.sqlite')
    )

    if test_config is None:
        # Cargar la instacia config, si existe, cuando no se esté probando
        app.config.from_pyfile('config.py', silent=True)
    else: 
        # Cargar la prueba config si la pasó
        app.config.from_mapping(test_config)
    
    # Asegurar que la instancia de la carpeta exista
    try: 
        os.makedirs(app.instance_path)
    except OSError: 
        pass

    # Una simple página de hola
    @app.route('/hola')
    def hola():
        return '¡Hola mundo!'
    
    import db

    db.init_app(app)

    import auth

    app.register_blueprint(auth.bp)

    import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app