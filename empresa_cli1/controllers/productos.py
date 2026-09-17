from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from empresa_cli1.models import Producto
from empresa_cli1.db import db

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

@productos_bp.route("/")
@login_required
def lista_productos():
    productos = Producto.query.all()
    return render_template("productos/lista.html", productos=productos)

@productos_bp.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar_producto():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        existencia = request.form.get("existencia")

        nuevo = Producto(nombre=nombre, precio=float(precio), existencia=int(existencia))
        db.session.add(nuevo)
        db.session.commit()

        flash("Producto agregado con éxito", "success")
        return redirect(url_for("productos.lista_productos"))

    return render_template("productos/agregar.html")
