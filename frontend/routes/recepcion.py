from flask import Blueprint
from flask import render_template

admin_routes = Blueprint('rutas_prefijo_api', __name__)

@admin_routes.route('/')
def home():
    return  render_template('/admin/login.html')

@admin_routes.route('/')
def home():
    return  render_template('/admin/login.html')