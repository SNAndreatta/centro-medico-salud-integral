from flask import Blueprint
from flask import render_template

auth_routes = Blueprint('rutas_prefijo_api', __name__)

@auth_routes.route('/login')
def login():
    return  render_template('/auth/login.html')

@auth_routes.route('/register')
def register():
    return  render_template('/auth/register.html')