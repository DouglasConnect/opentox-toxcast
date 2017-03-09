#!/usr/bin/env python3

'''
Usage:
  app.py [--debug]

Options:
  -h --help     Show this screen.
  -d --debug    Enable debug mode and autoreload on code changes.
'''

import connexion
from docopt import docopt
from flask_cors import CORS
from flask import redirect

# Patch yaml loader to preserve key order
import yaml
import ruamel.yaml
yaml.load = lambda stream, Loader: ruamel.yaml.load(stream, Loader=ruamel.yaml.RoundTripLoader)

if __name__ == '__main__':
    args = docopt(__doc__)
    app = connexion.App(__name__, specification_dir='./swagger/')

    CORS(app.app)
    app.app.config['JSON_SORT_KEYS'] = False

    app.add_api(
        'swagger.yaml',
        arguments={
            'title': 'This Api exposes the EPA\'s ToxCast summary dataset (October 2015 release). ToxCast contains data for a single chemical endpoint pair for thousands of chemicals and 821 assay endpoints for 20 variables such as the activity or hit call, activity concentrations, whether the chemical was tested in a specific assay, etc.'
        })

    @app.route('/')
    def index():
        return redirect('/beta/ui/')

    app.run(host='0.0.0.0', port=8080, debug=args['--debug'])
