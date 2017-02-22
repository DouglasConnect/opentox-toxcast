# ToxCast Tox21 API

This is the API implementation to expose the ToxCast data. It uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask. A scaffold for this implementation was built from the OpenAPI/Swagger definition.

## Setup

Requirements:

- Elasticsearch 2.3 running
- Python 3
- Python requirements from requirements.txt

To install python requirements (preferably inside [pyvenv](https://virtualenv.pypa.io/en/stable/)) run:

    pip install -r requirements.txt --upgrade

Running the api server

    python app.py

## Rerunning the swagger-codegen tool after big schema changes

If you make major changes to the swagger definition (e.g. add a new endpoint, change parameters etc), rather than add these by hand you can run the swagger-codegen tool again. When you do so, the existing implementation will be overwritten, so make sure to have a clean working copy of this repo before you run the tool, so you can use `git checkout OVERWRITTEN-FILES` to undo the changes that deleted the existing implementation.

At the root of this repository, run:

    java -jar swagger-codegen-cli.jar generate -l python-flask -i Swagger.yaml -o api
