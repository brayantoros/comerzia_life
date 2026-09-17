from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from empresa_cli1.models import Usuario
from empresa_cli1.db import db

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

# Lista de usuarios (solo admins)
@usuarios_bp.route("/")
@login_required
def lista_usuarios():
    if current_user.rol != "admin":
        flash("No tienes permisos para ver esta página", "danger")
        return redirect(url_for("main.index"))
    usuarios = Usuario.query.all()
    return render_template("usuarios/lista.html", usuarios=usuarios)

# Crear usuario (solo admins)
@usuarios_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear_usuario():
    if current_user.rol != "admin":
        flash("No tienes permisos para crear usuarios", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        nombre = request.form.get("nombre")
        nombre_usuario = request.form.get("nombre_usuario") or request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol") or "cliente"

        nuevo = Usuario(
            nombre=nombre or nombre_usuario,
            nombre_usuario=nombre_usuario,
            email=email,
            clave=generate_password_hash(password),
            rol=rol
        )
        db.session.add(nuevo)
        db.session.commit()

        flash("Usuario creado con éxito", "success")
        return redirect(url_for("usuarios.lista_usuarios"))

    return render_template("usuarios/crear.html")