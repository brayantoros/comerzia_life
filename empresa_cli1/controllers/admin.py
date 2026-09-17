from flask import Blueprint

admin = Blueprint('admin', __name__)

@admin.route('/admin')
def panel_admin():
    return "Panel del administrador"
