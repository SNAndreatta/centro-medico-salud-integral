from flask import Blueprint
from flask import render_template

recepcion_routes = Blueprint('rutas_recepcion_prefijo_api', __name__)

@recepcion_routes.route('/r')
def home():
    return render_template('/recepcion/home.html')
