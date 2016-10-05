#!/usr/bin/env python3

import connexion

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'This Api exposes the EPA&#39;s ToxCast summary dataset (October 2015 release).  ToxCast contains data for a single chemical endpoint pair for thousands of chemicals and 821 assay endpoints for 20 variables such as the activity or hit call, activity concentrations, whether the chemical was tested in a specific assay, etc. '})
    app.run(port=8080)
