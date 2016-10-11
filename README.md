# OpenTox • ToxCast

## API

To recreate the api after an upodate to the swagger definition, either copy the content of the swagger file in this directory into the [online swagger editor](http://editor.swagger.io/#/) and download a generated server api (python flask) or use the command line tool from the [swagger codegen page](https://github.com/swagger-api/swagger-codegen). The generated batch of files can then be dropped into ./api, but take care not to overwrite default_controllers.py which contains the code to serve the various endpoints (but incorporating changes if endpoints were modified).

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
