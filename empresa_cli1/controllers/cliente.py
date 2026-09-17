from flask import Blueprint, render_template

cliente = Blueprint('cliente', __name__, url_prefix='/cliente')

@cliente.route('/')
def inicio_cliente():
    return "Inicio Cliente"
