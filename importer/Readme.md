# ToxCast and Tox21 summary data importer

This code takes care of downloading the official ToxCast/Tox21 summary release, unzipping it and parsing the csv files and feeding it into Elasticsearch.

Since we anticipate the summary release schema to change in future versions, every official release will get it's own pair of parser schema definition (releases/2015-10-20/parser-schema.yaml) and elastic search mapping (releases/2015-10-20/elastic-mapping.yaml). These two are just simple YAML files that describe the columns of the csv file (including NaN identifiers used) and the mapping of those to JSON objects for storage in ElasticSearch respectively.

## Setup

Requirements:

- Elasticsearch 2.3 running
- Python 3
- Python requirements from requirements.txt

To install python requirements (preferably inside [pyvenv](https://virtualenv.pypa.io/en/stable/)) run:

    pip install -r requirements.txt --upgrade

## ToxCast data importer for Elasticsearch

ToxCast data importer is designed around ToxCast summary files releases where each ToxCast release has a separate parser and ElasticSearch mapping config files.

To see help on how to use the importer run (including Elasticsearch index management):

    ./importer/importer.py --help

Examples:

    ./importer/importer.py elastic index create toxcast importer/releases/release/elastic-mapping.yaml

    ./importer/importer.py import toxcast /path/to/toxcast/release/ importer/releases/release/parser-schema.yaml

    ./importer/importer.py elastic index drop toxcast
