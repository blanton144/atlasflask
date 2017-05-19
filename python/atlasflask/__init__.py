#!/usr/bin/python

from __future__ import print_function
from __future__ import division

import os
import sys
import socket
# import psycopg2
from inspect import getmembers, isfunction

import flask

import atlasflask.jinja_filters as jinja_filters
# from .color_print import print_warning, print_error, print_info

# creates the app instance using the name of the module
# app = Flask(__name__)

# -----------------------------------------
# The snippet below is to hide the warning:
# /usr/local/python/lib/python2.7/site-packages/sqlalchemy/engine/reflection.py:40: SAWarning: Skipped unsupported reflection of expression-based index q3c_spectrum_idx
# WARNING: SAWarning: Skipped unsupported reflection of expression-based index q3c_psc_idx [sqlalchemy.util.langhelpers]
# -----------------------------------------
import warnings
warnings.filterwarnings(action="ignore",
                        message="Skipped unsupported reflection")
warnings.filterwarnings(action="ignore",
                        message='Predicate of partial index')


def create_app(debug=False, dev=False):
    """
    Create a Petunia Flask app.
    Set debug when running outside of uwsgi.
    Set dev to connect to the dev database.
    Set asPort None or an interger on which port the as runs.
    """
    app = flask.Flask(__name__)

    app.debug = debug

    print("{0}App '{1}' created.{2}".format('\033[92m',
                                            __name__,
                                            '\033[0m'))  # to remove later

    # Define custom filters into the Jinja2 environment.
    # Any filters defined in the jinja_env submodule are made available.
    # See: http://stackoverflow.com/questions/12288454/how-to-import-custom-jinja2-filters-from-another-file-and-using-flask
    custom_filters = {name: function
                      for name, function in getmembers(jinja_filters)
                      if isfunction(function)}
    app.jinja_env.filters.update(custom_filters)

    # if app.debug == False:
    # Actually don't do this at all ... yet
    if 0:
        # ----------------------------------------------------------
        # Set up getsentry.com logging - only use when in production
        # ----------------------------------------------------------
        from raven.contrib.flask import Sentry

        dsn = 'https://dfc79fd911a9481e9b22321e63689238:27f7bbb75c834c3385f171632e745516@app.getsentry.com/29279'
        app.config['SENTRY_DSN'] = dsn
        sentry = Sentry(app)
        # --------------------------------------
        # Configuration when running under uWSGI
        # --------------------------------------
        try:
            import uwsgi
            app.use_x_sendfile = True
        except ImportError:
            # not running under uWSGI (and presumably, nginx)
            pass

    # Change the implementation of "decimal" to a
    # C-based version (much! faster)
    try:
        import cdecimal
        sys.modules["decimal"] = cdecimal
    except ImportError:
        pass  # no available

    # ------------------------------------------------------------------
    # The JSON module is unable to serialize Decimal objects, which is
    # a problem as psycopg2 returns Decimal objects for numbers. This
    # block of code overrides how psycopg2 parses decimal data types
    # coming from the database, using the "float" data type instead of
    # Decimal. This must be done separately for array data types.
    #
    # See link for other data types:
    #   http://initd.org/psycopg/docs/extensions.html
    # -------------------------------------------------------------------
    #DEC2FLOAT = psycopg2.extensions.new_type(
        #psycopg2.extensions.DECIMAL.values,
        #'DEC2FLOAT',
        #lambda value, curs: float(value) if value is not None else None)
    #psycopg2.extensions.register_type(DEC2FLOAT)
#
    ## the decimal array is returned as a string in the form:
    ## "{1,2,3,4}"
    #DECARRAY2FLOATARRAY = psycopg2.extensions.new_type(
        #psycopg2.extensions.DECIMALARRAY.values,
        #'DECARRAY2FLOATARRAY',
        #lambda value, curs: [float(x) if x else None for x in value[1:-1].split(",")] if value else None)
    ##    lambda value, curs: sys.stdout.write(value))
    #psycopg2.extensions.register_type(DECARRAY2FLOATARRAY)
    # ------------------------------------------------------------------

    # Determine which configuration file should be loaded based on which
    # server we are running on. This value is set in the uWSGI config file
    # for each server.

    if app.debug:  # args['debug']:
        hostname = socket.gethostname()
        if "sdss.utah.edu" in hostname:
            if dev is False:
                server_config_file = os.path.join(os.getenv('ATLASFLASK_DIR'),
                                                  'etc',
                                                  'sdss.utah.edu.cfg')
            else:
                server_config_file = os.path.join(os.getenv('ATLASFLASK_DIR'),
                                                  'etc',
                                                  'dev-sdss.utah.edu.cfg')
        else:
            server_config_file = os.path.join(os.getenv('ATLASFLASK_DIR'),
                                              'etc', 'localhost.cfg')
    else:
        try:
            import uwsgi
            # The uwsgi configuration file defines a key value pair to point
            # to a particular configuration file in this module under
            # "configuration_files". The key is 'flask_config_file',
            # and the value is the name of the configuration file.
            server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'configuration_files',
                                              uwsgi.opt['flask-config-file'])
        except ImportError:
            print("Trying to run in production mode, but not running under uWSGI.\n"
                  "You might try running again with the '--debug' flag.")
            sys.exit(1)

    print("Loading config file: {0}".format(server_config_file))
    app.config.from_pyfile(server_config_file)

    # print(app.config)
    print("Server_name = {0}".format(app.config["SERVER_NAME"]))
    # for key, val in app.config.iteritems():
    #     print("%s = %s"%(key, val))
    # This "with" is necessary to prevent exceptions of the form:
    #    RuntimeError: working outside of application context
    #    (i.e. the app object doesn't exist yet - being created here)
    # NO db for the moment
    # with app.app_context():
    #    from .model.database import db

    # -------------------
    # Register blueprints
    # -------------------
    from .controllers.atlas import atlas_page
    from .controllers.index import index_page
    from .controllers.data import data_page
    from .controllers.documentation import documentation_page
    from .controllers.caveats import caveats_page
    from .controllers.credits import credits_page
    from .controllers.publications import publications_page
    from .controllers.search import search_page
#    from .controllers import getTemplateDictBase

    app.register_blueprint(atlas_page)
    app.register_blueprint(index_page)
    app.register_blueprint(data_page)
    app.register_blueprint(documentation_page)
    app.register_blueprint(caveats_page)
    app.register_blueprint(search_page)
    app.register_blueprint(publications_page)
    app.register_blueprint(credits_page)

    # @app.errorhandler(500)
    # def err_page(e):
        # """ Err page. """
        # return flask.render_template("500.html", **getTemplateDictBase())

    return app

# Perform early app setup here.
