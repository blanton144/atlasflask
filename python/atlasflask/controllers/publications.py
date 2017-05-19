import flask
from flask import render_template#, send_from_directory

from . import getTemplateDictBase

publications_page = flask.Blueprint("publications_page", __name__)


@publications_page.route('/publications')
def publications():
    """ Index page. """
    templateDict = getTemplateDictBase()
    templateDict['urldata'] = 'http://data.sdss.org/sas/dr13/sdss/atlas/v1'
    templateDict['atlasflaskVersion'] = 'XX'
    return render_template("publications.html", **templateDict)
