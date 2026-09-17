from flask import Flask, render_template
from flask_login import LoginManager
from empresa_cli1.db import db
from empresa_cli1.models import Usuario
from empresa_cli1.controllers import register_blueprints
from empresa_cli1.config import Config   # 👈 importa tu Config

login_manager = LoginManager()
login_manager.login_view = "autusuarios.login"

def create_app():
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(Config)  # 👈 carga las variables del config.py

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints
    register_blueprints(app)

    # Manejadores de errores básicos
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app