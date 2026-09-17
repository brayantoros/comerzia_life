from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from empresa_cli1.models import Usuario
from empresa_cli1.db import db

autusuarios_bp = Blueprint("autusuarios", __name__, url_prefix="/auth")

@autusuarios_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre_usuario = request.form.get("nombre_usuario") or request.form.get("username")
        correo = request.form.get("correo") or request.form.get("email")
        password = request.form.get("password") or request.form.get("clave")

        # Permitir login por nombre_usuario o por correo
        user = None
        if nombre_usuario:
            user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if not user and correo:
            user = Usuario.query.filter_by(email=correo).first()

        if user and check_password_hash(user.clave, password):
            if not user.activo:
                flash("Tu cuenta está inactiva. Contacta al administrador.", "warning")
                return redirect(url_for("autusuarios.login"))
            login_user(user)
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("autusuarios.dashboard"))
        else:
            flash("Credenciales inválidas", "danger")
            return redirect(url_for("autusuarios.login"))

    # GET
    return render_template("auth/login.html")

@autusuarios_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("main.index"))

@autusuarios_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        nombre_usuario = request.form.get("nombre_usuario") or request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password") or request.form.get("clave")

        existente = Usuario.query.filter(
            (Usuario.nombre_usuario == nombre_usuario) | (Usuario.email == email)
        ).first()
        if existente:
            flash("Usuario o correo ya registrado", "warning")
            return redirect(url_for("autusuarios.registro"))

        nuevo = Usuario(
            nombre=nombre or nombre_usuario,
            nombre_usuario=nombre_usuario,
            email=email,
            clave=generate_password_hash(password),
            activo=True
        )
        db.session.add(nuevo)
        db.session.commit()
        flash("Usuario creado. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("autusuarios.login"))

    return render_template("usuarios/crear.html")

# Dashboard luego del login
@autusuarios_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("base_inicio.html", usuario=current_user)