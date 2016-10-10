# OpenTox • ToxCast

## API

TODO: describe how to create an API from the swagger definition

## ToxCast data importer for Elasticsearch

ToxCast data importer is designed around ToxCast summary files releases where each ToxCast release has a separate parser and ElasticSearch mapping config files.

To see help on how to use the importer run (including Elasticsearch index management):

    ./importer/importer.py --help

Examples:

    ./importer/importer.py elastic index create toxcast importer/releases/2015-10-20/elastic-mapping.yaml

    ./importer/importer.py import toxcast /path/to/INVITRODB_V2_SUMMARY/ importer/releases/2015-10-20/parser-schema.yaml

    ./importer/importer.py elastic index drop toxcast

## Setup

Requirements:

- Elasticsearch 2.3
- Python 2.7
- Python requirements from requirements.txt

To install python requirements (preferably inside [virtualenv](https://virtualenv.pypa.io/en/stable/)) run:

    pip install -r requirements.txt --upgrade

## Example Elasticsearch queries

### Assays

Get all assays:

    GET /toxcast/assay/_search
    {
      "query": {
        "match_all": {}
      }
    }

### Compounds

Get all compounds:

    GET /toxcast/compound/_search
    {
      "query": {
        "match_all": {}
      }
    }

### Results

Get all results:

    GET /toxcast/result/_search
    {
      "query": {
        "match_all": {}
      }
    }

Aggregate on `hitc`:

    GET /toxcast/result/_search
    {
      "size": 0,  
      "aggs": {
        "hitc": {
          "terms": {
            "field": "result.hitc"
          }
        }
      }
    }
