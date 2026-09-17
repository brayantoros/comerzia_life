from .main import main
from .autusuarios import autusuarios_bp
from .admin import admin
from .cliente import cliente
from .productos import productos_bp
from .usuarios import usuarios_bp

def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(autusuarios_bp)
    if 'admin' in globals() and admin:
        app.register_blueprint(admin)
    if 'cliente' in globals() and cliente:
        app.register_blueprint(cliente)
    app.register_blueprint(productos_bp)
    app.register_blueprint(usuarios_bp)