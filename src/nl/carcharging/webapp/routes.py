from flask import Blueprint, render_template, abort
from jinja2.exceptions import TemplateNotFound

""" 
 - make sure all url_for routes point to this blueprint
"""
webapp = Blueprint('webapp', __name__, template_folder='templates')

@webapp.route('/', methods=['GET'])
def index():
    try:
        return render_template('dashboard.html')
    except TemplateNotFound:
        abort(404)

@webapp.route("/home")
#@authenticated_resource
def home():
    try:
        return render_template('dashboard.html')
    except TemplateNotFound:
        abort(404)


@webapp.errorhandler(404)
def page_not_found(e):
    return render_template('errorpages/404.html'), 404
