from flask import Blueprint

bp = Blueprint('general', __name__, template_folder='templates')

from app.general import routes
