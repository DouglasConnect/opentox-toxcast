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


if __name__ == '__main__':
    args = docopt(__doc__)
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'This Api exposes the EPA&#39;s ToxCast summary dataset (October 2015 release). ToxCast contains data for a single chemical endpoint pair for thousands of chemicals and 821 assay endpoints for 20 variables such as the activity or hit call, activity concentrations, whether the chemical was tested in a specific assay, etc.'})
    CORS(app.app)
    app.run(host='0.0.0.0', port=8000, debug=args['--debug'])
