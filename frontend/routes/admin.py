from flask import Blueprint
from flask import render_template

admin_routes = Blueprint('rutas_prefijo_api', __name__)

@admin_routes.route('/')
def home():
    return  render_template('/admin/login.html')

@admin_routes.route('/profile')
def profile():
    return  render_template('/admin/register.html')

@admin_routes.route('/abm-usuario')
def usuario():
    return  render_template('/admin/register.html')

@admin_routes.route('/abm-medico')
def medico():
    return  render_template('/admin/register.html')

@admin_routes.route('/abm-consultorio')
def consultorio():
    return  render_template('/admin/register.html')

@admin_routes.route('/abm-especialidad')
def especialidad():
    return  render_template('/admin/register.html')

@admin_routes.route('/abm-cobertura')
def cobertura():
    return  render_template('/admin/register.html')

@admin_routes.route('/sala-de-espera')
def dashboards():
    return  render_template('/admin/register.html')