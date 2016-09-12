#!/usr/bin/env python

'''
Usage:
    toolbox.py enumerate <filename>
    toolbox.py yaml-to-json <filename>
    toolbox.py json-to-yaml <filename>
    toolbox.py elastic index create <index> <index.yaml> [--elasticsearchhost=<hostname>]
    toolbox.py elastic index delete <index> [--elasticsearchhost=<hostname>]
    toolbox.py elastic index exists <index> [--elasticsearchhost=<hostname>]
    toolbox.py elastic data load <index> <parser-schema.yaml> <assays.csv> <compounds.csv> <results.csv>... [--elasticsearchhost=<hostname>] [--identifierconverter=<hostname>] [--without-chemid-conversion]

Options:
  -h --help  Show this help.
  -e <hostname> --elasticsearchhost=<hostname>  Specify the hostname of the elastic search host. Default is localhost.
  -i <hostname> --identifierconverter=<hostname>  Specify the hostname of the chemical identifier conversion tool (chemiDConvert). Default is localhost.
  --without-chemid-conversion  Do not perform additional chemical identifier conversions. Default is to perform the conversions.
'''

import csv
import yaml
import json
import logging
import sys
import requests
import re

logging.basicConfig(format='%(levelname)s %(message)s')
logging.getLogger('__main__').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

from docopt import docopt
from elasticsearch import Elasticsearch, ElasticsearchException


# -----------------------------------------------------------------------------
# YAML / JSON

def load_yaml_file(filename):
    with open(filename, 'r') as fi:
        return yaml.load(fi)


def yaml_to_json(filename, indent=2):
    return json.dumps(load_yaml_file(filename), indent=indent)


def json_to_yaml(filename, indent=2):
    with open(filename, 'r') as fi:
        print yaml.dump(yaml.load(json.dumps(json.load(fi))))


# -----------------------------------------------------------------------------
# Enumerate

def enum(filename):
    with open(filename, 'r') as fi:
        for i, line in enumerate(fi):
            pass
            # print i, line,


# -----------------------------------------------------------------------------
# Elastic index

def elastic_index_create(es, index, definition):
    es.indices.create(index=index, body=definition)


def elastic_index_delete(es, index):
    es.indices.delete(index=index)


def elastic_index_exists(es, index):
    return es.indices.exists(index=index)


# -----------------------------------------------------------------------------
# Data parsing and importing into Elastic

class ParseError(Exception):
    pass


class CSVParser(object):

    def __init__(self, schema, start_at_row):
        self.schema = schema
        self.start_at_row = start_at_row

    def parse(self, filename):
        with open(filename, 'rb') as fi:
            reader = csv.reader(fi)
            for i, line in enumerate(reader):
                if i >= self.start_at_row:
                    yield(self.parse_line(filename, i, line))

    def parse_line(self, filename, i, line):
        try:
            return dict([(key, self.parse_value(schema, line)) for key, schema in self.schema.items()])
        except Exception, e:
            logger.warn('Error parsing file %s at line %s: %s)' % (filename, i, e))
            return None

    def parse_value(self, schema, line):
        value = line[schema['col']]
        nulls = schema.get('nulls', None)

        if nulls is not None and value in nulls:
            return None

        if schema['type'] == 'string':
            return self.parse_string(value, nulls)
        elif schema['type'] == 'integer':
            return self.parse_integer(value, nulls)
        else:
            raise ParseError('unknown property type: \'%s\'' % schema['type'])

    def parse_string(self, value, nulls=None):
        return value.strip()

    def parse_integer(self, value, nulls=None):
        return int(value.strip())


class Parser(object):

    def __init__(self, schema):
        self.schema = schema

    def parse_assays(self, filename):
        return CSVParser(self.schema['assay']['properties'], self.schema['assay'].get('startAtRow', 0)).parse(filename)

    def parse_compounds(self, filename):
        return CSVParser(self.schema['compound']['properties'], self.schema['compound'].get('startAtRow', 0)).parse(filename)

    def parse_results(self, filename):
        return CSVParser(self.schema['result']['properties'], self.schema['result'].get('startAtRow', 0)).parse(filename)


def queryAdditionalIdentifiers(identifierconverter, casnr):
    if not re.match('^\d+-\d+-\d+$', casnr):
        logger.error('Not a valid cas number: %s' % casnr)
        return None

    r = requests.get('http://%s/v1/cas/to/inchi' % identifierconverter, params={'cas': casnr})
    if r.status_code != 200 or r.json()['inchi'] is None:
        logger.error('Could not convert cas number: %s' % casnr)
        return None

    inchi = r.json()['inchi']

    r = requests.get('http://%s/v1/inchi/to/inchikey' % identifierconverter, params={'inchi': inchi})
    if r.status_code != 200 or r.json()['inchikey'] is None:
        logger.error('Could not convert to inchikey?! %s' % inchi)
        return None

    inchikey = r.json()['inchikey']

    r = requests.get('http://%s/v1/inchi/to/smiles' % identifierconverter, params={'inchi': inchi})
    if r.status_code != 200 or r.json()['smiles'] is None:
        logger.error('Could not convert to smiles?! %s' % inchi)
        return None

    smiles = r.json()['smiles']

    result = {
        'casn': casnr,
        'inchi': inchi,
        'inchikey': inchikey,
        'smiles': smiles
    }

    logger.debug('Converted %(casn)s to inchi %(inchi)s, inchikey %(inchikey)s and smiles %(smiles)s' % result)

    return result


def annotate_with_identifiers(identifierconverter, compound):
    additional_identifiers = queryAdditionalIdentifiers(identifierconverter, compound['casn'])
    if additional_identifiers is None:
        return compound
    else:
        result = compound.copy()
        result.update(additional_identifiers)
        return result


def elastic_load_data(es, identifierconverter, perform_chemid_conversion, index, parser_schema, assays_filename, compounds_filename, results_filenames):
    parser = Parser(parser_schema)

    assay_cache = {}
    compound_cache = {}

    # Assays
    logger.info('Parsing assays from %s' % assays_filename)
    for assay in parser.parse_assays(assays_filename):
        if assay is None:
            continue
        logger.debug('Indexing assay %s' % assay)
        es.index(index=index, doc_type='assay', body=assay)
        assay_cache[assay['aeid']] = assay

    # Compounds
    logger.info('Parsing compounds from %s' % compounds_filename)
    for compound in parser.parse_compounds(compounds_filename):
        if compound is None:
            continue
        logger.debug('Indexing compound %s' % compound)

        if perform_chemid_conversion:
            compound = annotate_with_identifiers(identifierconverter, compound)

        es.index(index=index, doc_type='compound', body=compound)
        compound_cache[compound['chid']] = compound

    # Results
    for filename in results_filenames:
        logger.info('Parsing results from %s' % filename)
        for result in parser.parse_results(filename):
            if result is None:
                continue
            logger.debug('Indexing result %s' % result)

            chid = result.get('chid', None)
            compound = None
            if chid is not None:
                compound = compound_cache.get(chid, None)

            if compound is None:
                logger.error('Found a result with unknown compound: %s' % chid)
                compound = {
                    'chid': result.get('chid'),
                    'chnm': result.get('chnm'),
                    'casn': result.get('casn'),
                }

            body = {
                'assay': assay_cache[result.get('aeid')],
                'compound': compound,
                'result': {
                    'hitc': result.get('hitc'),
                }
            }
            es.index(index=index, doc_type='result', body=body)


# -----------------------------------------------------------------------------
# Main

def main(argv=None):

    args = docopt(__doc__)

    elasticsearchhost = args.get('--elasticsearchhost', 'localhost')
    identifierconverter = args.get('--identifierconverter', 'localhost')
    perform_chemid_conversion = not args.get('--without-chemid-conversion', False)

    try:
        es = Elasticsearch(elasticsearchhost, timeout=30)
    except ElasticsearchException as e:
        print(e)
        sys.exit(2)

    if args['enumerate']:
        enum(args['<filename>'])

    elif args['yaml-to-json']:
        print yaml_to_json(args['<filename>'])

    elif args['json-to-yaml']:
        print json_to_yaml(args['<filename>'])

    elif args['elastic'] and args['index'] and args['create']:
        elastic_index_create(es, args['<index>'], load_yaml_file(args['<index.yaml>']))

    elif args['elastic'] and args['index'] and args['delete']:
        elastic_index_delete(es, args['<index>'])

    elif args['elastic'] and args['index'] and args['exists']:
        if elastic_index_exists(es, args['<index>']):
            logger.info('Using existing Elastic index')
        else:
            logger.error('Elastic index does not exist')
            sys.exit(1)  # Return a non-zero return code for downstream shell scripts

    elif args['elastic'] and args['load'] and args['data']:
        elastic_load_data(
            es,
            identifierconverter,
            perform_chemid_conversion,
            args['<index>'],
            load_yaml_file(args['<parser-schema.yaml>']),
            args['<assays.csv>'],
            args['<compounds.csv>'],
            args['<results.csv>']
        )

if __name__ == '__main__':
    main()

# -----------------------------------------------------------------------------
