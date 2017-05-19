import flask
from flask import render_template#, send_from_directory

from . import getTemplateDictBase

search_page = flask.Blueprint("search_page", __name__)


@search_page.route('/search')
def search():
    """ Index page. """
    templateDict = getTemplateDictBase()
    templateDict['nsaid'] = 123456
    templateDict['urldata'] = 'http://data.sdss.org/sas/dr13/sdss/atlas/v1'
    templateDict['atlasflaskVersion'] = 'XX'
    templateDict['nsaid_max'] = 699999
    return render_template("search.html", **templateDict)
