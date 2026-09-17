from empresa_cli1.db import db
from empresa_cli1.models import Usuario
from sqlalchemy.exc import SQLAlchemyError

def get_user_by_id(user_id):
    try:
        return Usuario.query.get(user_id)
    except SQLAlchemyError as e:
        print(f"Error al obtener el usuario: {e}")
        return None

def get_all_users():
    try:
        return Usuario.query.all()
    except SQLAlchemyError as e:
        print(f"Error al obtener los usuarios: {e}")
        return []

def add_user(username, email, password_hash):
    try:
        new_user = Usuario(nombre_usuario=username, email=email, clave=password_hash)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error al agregar el usuario: {e}")
        return None

def delete_user(user_id):
    try:
        user = Usuario.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error al eliminar el usuario: {e}")
        return False

def toggle_user_status(user_id, active):
    try:
        user = Usuario.query.get(user_id)
        if user:
            user.activo = active
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error al actualizar estado: {e}")
        return False

def get_user_by_username(username):
    return Usuario.query.filter_by(nombre_usuario=username).first()
