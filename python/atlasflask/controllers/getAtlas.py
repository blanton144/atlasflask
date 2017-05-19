# -*- coding: utf-8 -*-
import numpy as np
import astropy.wcs as wcs
import json
import flask
import fitsio
import dimage.path as path
from flask import request, render_template
from PIL import Image
from . import getTemplateDictBase

"""
Controller for getAtlas.html page.
"""

# Initialize atlas connection; for the atlas we need it to be over
# http to generate the correct set of links
nsa = path.Path()
nsa.remote(username='sdss', password='2.5-meters')

# Placeholder for when there is a db to connect to
# (Though this possibly should live in the atlas.py module)
# from ..model.database import db

getAtlas_page = flask.Blueprint("getAtlas_page", __name__)


def processGetRequest(request):
    """
    @param[in] request: the flask.request element generated from the get request
    @return a dictionary containing values extracted from the request.
        note: some will be extraneous (and set to None) for the planObserving
        page.
    """
    return {
        "nsaid": request.args['nsaid'],
    }


class cutout:
    def __init__(self, xpos=None, ypos=None, xsize=None, ysize=None,
                 band=None, jpg=None):
        self.xpos = xpos
        self.ypos = ypos
        self.xsize = xsize
        self.ysize = ysize
        self.jpg = jpg
        self.band = band


def apply_bounds(x=None, xlim=None):
    ilow = np.nonzero(x < xlim[0])[0]
    if len(ilow) > 0:
        x[ilow] = xlim[0]
    ihigh = np.nonzero(x > xlim[1])[0]
    if len(ihigh) > 0:
        x[ihigh] = xlim[1]
    return x


def param2ellipse(racen, deccen, radius, ba, phi, nellipse=100):
    """
    @param[in] xcen: X center for ellipse
    @param[in] ycen: Y center for ellipse
    @param[in] radius: semi-major axis
    @param[in] ba: minor to major axis-ratio (b/a)
    @param[in] phi: position angle of ellipse (deg)
    @param[in] nellipse: number of points in ellipse (default 100)
    @return ellipse: 2-by-nellipse list
    """
    nellipse = 100
    theta = np.arange(nellipse) * np.pi * 2. / float(nellipse - 1)
    xellipse = ba * radius * np.cos(theta)
    yellipse = radius * np.sin(theta)
    xellipse_p = (xellipse * np.cos((180. - phi) * np.pi / 180.) -
                  yellipse * np.sin((180. - phi) * np.pi / 180.))
    yellipse_p = (- xellipse * np.sin((180. - phi) * np.pi / 180.) -
                  yellipse * np.cos((180. - phi) * np.pi / 180.))
    raellipse = xellipse_p / np.cos(deccen * np.pi / 180.) + racen
    decellipse = yellipse_p + deccen
    ellipse = [raellipse, decellipse]
    # this is how you transpose a list in python; awesome language fellas
    ellipse = map(list, zip(*ellipse))
    return ellipse


def image_info(image_file=None, racen=None, deccen=None,
               cutout_size_screen=None, cutout_size_deg=None,
               ext=0):
    image_hdr = fitsio.read_header(image_file, ext=ext)
    image_nx = np.int32(image_hdr['NAXIS1'])
    image_ny = np.int32(image_hdr['NAXIS2'])
    image_wcs = wcs.WCS(image_hdr)
    (image_xcen, image_ycen) = \
        image_wcs.all_world2pix(racen, deccen, 0)
    ntest = 10.
    (image_ratest, image_dectest) = \
        image_wcs.all_pix2world(image_xcen, image_ycen + ntest, 0)
    pixscale = (image_dectest - deccen) / ntest
    cutout_size_pix = cutout_size_deg / pixscale
    image_xsize = \
        np.int32(np.round(np.float32(image_nx) *
                          np.float32(cutout_size_screen) /
                          np.float32(cutout_size_pix)))
    image_ysize = \
        np.int32(np.round(np.float32(image_ny) *
                          np.float32(cutout_size_screen) /
                          np.float32(cutout_size_pix)))
    dxpos = ((np.float32(image_xcen) -
              0.5 * np.float32(image_nx)) *
             np.float32(image_xsize) /
             np.float32(image_nx))
    dypos = ((np.float32(image_ycen) -
              0.5 * np.float32(image_ny)) *
             np.float32(image_ysize) /
             np.float32(image_ny))
    image_xpos = \
        - np.int32(np.round(dxpos - 0.5 * np.float32(cutout_size_screen) +
                            0.5 * np.float32(image_xsize)))
    image_ypos = \
        - np.int32(np.round(- dypos - 0.5 * np.float32(cutout_size_screen) +
                            0.5 * np.float32(image_ysize)))
    return cutout(image_xpos[0], image_ypos[0], image_xsize[0], image_ysize[0])


@getAtlas_page.route('/getAtlas.html', methods=['GET'])
def getAtlas():
    """
    Controller for the getAtlas.html page
    """

    # No errors yet
    errorMsg = ""

    # Placeholder for db connection
    #    session = db.Session()

    # Process html request arguments and
    formElements = processGetRequest(request)
    try:
        nsaid = int(formElements['nsaid'])
    except:
        errorMsg = errorMsg + "Must supply NSAID (an integer) as an argument\n"
        return render_template("noAtlas.html", errorMsg)

    # Stuff elements into templateDict
    templateDict = getTemplateDictBase()
    templateDict.update(formElements)

    version = 'v1_0_0'
    cutout_size_screen = 300

    # Changes:
    #  * Calculate desired cutout size from th90
    #  * Read full mosaic image
    #  * Use CSS clip to restrict image
    #  * Calculate cutout size for each band
    #  * Use CSS clip with each band

    # Cutout name
    mosaic_jpg = nsa.url('mosaic_jpg',
                         version=version, nsaid=nsaid)

    # Get information about Petrosian fit
    petro = fitsio.read(nsa.get('petro', version=version, nsaid=nsaid))
    racen = petro['racen']
    deccen = petro['deccen']
    th50 = petro['petroth50_r']
    th90 = petro['petroth90_r']
    ba = petro['ba']
    phi = petro['phi']

    # Cutout size, in pixels
    cutout_size_deg = th90 * 4.5 / 3600.

    # Get information about full mosaic image
    mosaic_file = nsa.get('mosaic', version=version, nsaid=nsaid,
                          band='r')
    mosaic_cutout = \
        image_info(image_file=mosaic_file, racen=racen, deccen=deccen,
                   cutout_size_screen=cutout_size_screen,
                   cutout_size_deg=cutout_size_deg)
    mosaic_cutout.jpg = mosaic_jpg
    mosaic_cutout.band = 'irg'

    ellipse50 = param2ellipse(racen, deccen, th50 / 3600., ba, phi)
    ellipse90 = param2ellipse(racen, deccen, th90 / 3600., ba, phi)

    bands = ['fd', 'nd', 'u', 'g', 'r', 'i', 'z']
    band_order = [5, 6, 0, 1, 2, 3, 4]
    parents = []
    for iband in range(len(bands)):
        band = bands[iband]
        parent_jpg = nsa.url('parent_jpg',
                             version=version, nsaid=nsaid, band=band)
        parent_image_file = nsa.get('parent_image',
                                    version=version, nsaid=nsaid,
                                    band=band)
        parent_cutout = \
            image_info(image_file=parent_image_file, ext=band_order[iband],
                       racen=racen, deccen=deccen,
                       cutout_size_screen=cutout_size_screen,
                       cutout_size_deg=cutout_size_deg)
        parent_cutout.band = band
        parent_cutout.jpg = parent_jpg
        parents.append(parent_cutout)

    children = []
    for iband in range(len(bands)):
        band = bands[iband]
        child_jpg = nsa.url('atlas_jpg',
                            version=version, nsaid=nsaid, band=band)
        child_image_file = nsa.get('child_image',
                                   version=version, nsaid=nsaid,
                                   band=band)
        child_cutout = \
            image_info(image_file=child_image_file, ext=band_order[iband],
                       racen=racen, deccen=deccen,
                       cutout_size_screen=cutout_size_screen,
                       cutout_size_deg=cutout_size_deg)
        child_cutout.band = band
        child_cutout.jpg = child_jpg
        children.append(child_cutout)

    templateDict['racen'] = racen[0]
    templateDict['deccen'] = deccen[0]
    templateDict['bands'] = bands
    templateDict['mosaic'] = mosaic_cutout
    templateDict['ellipse90'] = json.dumps(ellipse90)
    templateDict['cutout_size_deg'] = cutout_size_deg[0]
    templateDict['parents_and_children'] = zip(parents, children)
    templateDict['atlasflaskVersion'] = 'XX'
    return render_template("getAtlas.html", **templateDict)

if __name__ == "__main__":
    pass
