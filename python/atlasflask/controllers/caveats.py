import flask
from flask import render_template#, send_from_directory

from . import getTemplateDictBase

caveats_page = flask.Blueprint("caveats_page", __name__)


@caveats_page.route('/caveats')
def caveats():
    """ Index page. """
    templateDict = getTemplateDictBase()
    templateDict['urldata'] = 'http://data.sdss.org/sas/dr13/sdss/atlas/v1'
    templateDict['atlasflaskVersion'] = 'XX'
    return render_template("caveats.html", **templateDict)
