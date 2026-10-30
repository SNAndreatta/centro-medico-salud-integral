from flask import Blueprint
from flask import render_template

medico_routes = Blueprint('rutas_medico_prefijo_api', __name__)

@medico_routes.route('/r')
def home():
    return render_template('/medico/home.html')