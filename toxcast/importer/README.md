# ToxCast

ToxCast data importer for elasticsearch.

`toolbox.py` command provides functionality to import ToxCast data into elasticsearch. Type './toolboxy.py' or `python toolbox.py` for usage. Also see below.

`elsatic` directory contains elasticsearch mapping file `index.yaml` and ToxCast esport files parser shema `parser-schema.yaml`. Currently, only a subset of assay and result data columns are used.


## Requirements

- Elasticsearch 2.3
- Python 2.7
- Python requirements from requirements.txt

To install python requirements (preferably inside [virtualenv](https://virtualenv.pypa.io/en/stable/)) run:

    pip install -r requirements.txt --upgrade


## ToxCast data importer

To delete an existing elasticsearch index:

    ./toolbox.py elastic index delete toxcast

To create an elasticsearch index:

    ./toolbox.py elastic index create toxcast elastic/index.yaml

To import ToxCast data into elasticsearch:

    ./toolbox.py elastic data load toxcast elastic/parser-schema.yaml Assay_Summary.csv Chemical_Summary.csv EXPORT_1.csv EXPORT_2.csv ...


## Elasticsarch example queries

### Schema (mapping)

    GET /toxcast/_mapping

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
