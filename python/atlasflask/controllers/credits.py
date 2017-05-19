import flask
from flask import render_template#, send_from_directory

from . import getTemplateDictBase

credits_page = flask.Blueprint("credits_page", __name__)


@credits_page.route('/credits')
def credits():
    """ Index page. """
    templateDict = getTemplateDictBase()
    templateDict['urldata'] = 'http://data.sdss.org/sas/dr13/sdss/atlas/v1'
    templateDict['atlasflaskVersion'] = 'XX'
    return render_template("credits.html", **templateDict)
