import flask
from flask import render_template#, send_from_directory

from . import getTemplateDictBase

index_page = flask.Blueprint("index_page", __name__)


@index_page.route('/')
@index_page.route('/index.html')
def index():
    """ Index page. """
    return render_template("index.html", **getTemplateDictBase())
