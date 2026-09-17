from werkzeug.security import generate_password_hash, check_password_hash
from empresa_cli1.db import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    clave = db.Column(db.String(200), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    rol = db.Column(db.String(20), default="cliente")  # admin / cliente

    def set_password(self, password):
        self.clave = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.clave, password)

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'

    def get_id(self):
        return str(self.id)  # requerido por Flask-Login

class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    existencia = db.Column(db.Integer, default=0)
