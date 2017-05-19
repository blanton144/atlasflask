import flask
from flask import render_template#, send_from_directory

from . import getTemplateDictBase

data_page = flask.Blueprint("data_page", __name__)


@data_page.route('/data')
def data():
    """ Index page. """
    templateDict = getTemplateDictBase()
    templateDict['urldata'] = 'http://data.sdss.org/sas/dr13/sdss/atlas/v1'
    templateDict['atlasflaskVersion'] = 'XX'
    return render_template("data.html", **templateDict)
