import flask
from flask import render_template#, send_from_directory

from . import getTemplateDictBase

documentation_page = flask.Blueprint("documentation_page", __name__)


@documentation_page.route('/documentation')
def documentation():
    """ Index page. """
    templateDict = getTemplateDictBase()
    templateDict['urldata'] = 'http://data.sdss.org/sas/dr13/sdss/atlas/v1'
    templateDict['atlasflaskVersion'] = 'XX'
    return render_template("documentation.html", **templateDict)
