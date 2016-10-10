#!/usr/bin/env python

'''
Usage:
    importer.py elastic index create <index> <index.yaml> [--elasticsearch-host=<hostname>]
    importer.py elastic index drop <index> [--elasticsearch-host=<hostname>]
    importer.py elastic index exists <index> [--elasticsearch-host=<hostname>]
    importer.py import <index> <dirname> <parser-schema.yaml> [--elasticsearch-host=<hostname>] [--chemid-conversion-host=<hostname>] [--without-chemid-conversion]

Options:
  -h --help  Show this help.
  -e <hostname> --elasticsearch-host=<hostname>      Hostname of the elastic search host. Default is localhost.
  -i <hostname> --chemid-conversion-host=<hostname>  Hostname of the chemical identifier conversion tool (chemIdConvert). Default is localhost.
  --without-chemid-conversion                        Do not perform chemical identifier conversion. Default is to perform the conversion.
'''

import os
import sys
import re
import csv
import yaml
import math
import codecs
import logging
import requests

logging.basicConfig(format='%(levelname)s %(message)s')
logging.getLogger('__main__').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

from docopt import docopt
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch, ElasticsearchException


# -----------------------------------------------------------------------------
# Utilities

def load_yaml_file(filename):
    with open(filename, 'r') as fi:
        return yaml.load(fi)


# -----------------------------------------------------------------------------
# Elastic index

def elastic_index_create(es, index, definition):
    es.indices.create(index=index, body=definition)


def elastic_index_delete(es, index):
    es.indices.delete(index=index)


def elastic_index_exists(es, index):
    return es.indices.exists(index=index)


# -----------------------------------------------------------------------------
# Query chemical identifiers

class ChemIdConversionError(Exception):
    pass


def query_additional_chemical_identifiers(identifierconverter, casnr):
    if not re.match('^\d+-\d+-\d+$', casnr):
        logger.warn('Not a valid cas number: %s' % casnr)
        return None

    try:
        r = requests.get('http://%s/v1/cas/to/inchi' % identifierconverter, params={'cas': casnr})
        if r.status_code != 200 or r.json()['inchi'] is None:
            logger.warn('Could not convert cas number: %s' % casnr)
            return None
        inchi = r.json()['inchi']

        r = requests.get('http://%s/v1/inchi/to/inchikey' % identifierconverter, params={'inchi': inchi})
        if r.status_code != 200 or r.json()['inchikey'] is None:
            logger.warn('Could not convert to inchikey: %s' % inchi)
            return None
        inchikey = r.json()['inchikey']

        r = requests.get('http://%s/v1/inchi/to/smiles' % identifierconverter, params={'inchi': inchi})
        if r.status_code != 200 or r.json()['smiles'] is None:
            logger.warn('Could not convert to smiles: %s' % inchi)
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

    except requests.exceptions.ConnectionError, e:
        raise ChemIdConversionError(e)


# -----------------------------------------------------------------------------
# Data parsing and importing into Elastic

class ParseError(Exception):
    pass


class Parser(object):

    def __init__(self, dirname, schema):
        self.dirname = dirname
        self.schema = schema

    def abspath(self, filename):
        return os.path.abspath(os.path.join(self.dirname, filename))

    def parse_assays(self):
        return CSVParser(
            schema=self.schema['assays']['properties'],
            encoding=self.schema['assays'].get('encoding'),
            start_at_row=self.schema['assays'].get('startAtRow'),
        ).parse(self.abspath(self.schema['assays']['file']))

    def parse_compounds(self):
        return CSVParser(
            schema=self.schema['compounds']['properties'],
            encoding=self.schema['compounds'].get('encoding'),
            start_at_row=self.schema['compounds'].get('startAtRow')
        ).parse(self.abspath(self.schema['compounds']['file']))

    def parse_results(self):

        # get assays from the first results file (columns = assays)
        with codecs.open(self.abspath(self.schema['results'][0]['file']), 'rb', encoding=self.schema['results'][0].get('encoding', 'utf8')) as fi:
            for line in csv.reader((line.encode('utf8') for line in fi)):
                assays = line[1:]
                break

        result_parsers = [
            CSVParser(
                # generate schema from assay list
                schema=dict([('__COMPOUND__', {'col': 0, 'type': 'string'})] + [(assay, {'col': i + 1, 'type': result['type'], 'nulls': result['nulls']}) for i, assay in enumerate(assays)]),
                encoding=result.get('encoding'),
                start_at_row=result.get('startAtRow')
            ).parse(self.abspath(result.get('file'))) for result in self.schema['results']
        ]

        result_parts = [result['name'] for result in self.schema['results']]
        was_tested_result_part_index = result_parts.index('tested')

        try:
            while(True):
                # while we can read results files, combine lines from all results files and yield over assays
                line = [r.next() for r in result_parsers]
                compound = line[0]['__COMPOUND__']
                for assay in assays:
                    result = dict([(part, line[i][assay]) for i, part in enumerate(result_parts)])
                    # return data only if the assay was tested
                    if line[was_tested_result_part_index][assay]:
                        yield {
                            'compound': compound,
                            'assay': assay,
                            'result': result
                        }
        except StopIteration:
            pass


class CSVParser(object):

    def __init__(self, schema, encoding=None, start_at_row=None):
        self.schema = schema
        self.encoding = encoding if encoding is not None else 'utf8'
        self.start_at_row = start_at_row if start_at_row is not None else 0

    def parse(self, filename):
        with codecs.open(filename, 'rb', encoding=self.encoding) as fi:
            for i, line in enumerate(csv.reader((line.encode('utf8') for line in fi))):
                if i >= self.start_at_row:
                    yield(self.parse_line(filename, i, [x.decode('utf8') for x in line]))

    def parse_line(self, filename, i, line):
        try:
            return dict([(key, self.parse_value(schema, line)) for key, schema in self.schema.items()])
        except Exception, e:
            logger.warn('Error parsing file %s at line %s: %s' % (filename, i, e))
            return None

    def parse_value(self, schema, line):
        value = line[schema['col']]
        nulls = schema.get('nulls')

        if nulls is not None and value in nulls:
            return None

        if schema['type'] == 'string':
            return self.parse_string(value)
        elif schema['type'] == 'boolean':
            return self.parse_boolean(value)
        elif schema['type'] == 'integer':
            return self.parse_integer(value)
        elif schema['type'] == 'float':
            return self.parse_float(value)
        else:
            raise ParseError('unknown property type: \'%s\'' % schema['type'])

    def parse_string(self, value):
        return value.strip()

    def parse_boolean(self, value):
        if int(value.strip()) in [0, 1]:
            return bool(int(value.strip()))
        else:
            raise ParseError('invalid value for bool: %s' % value)

    def parse_integer(self, value):
        try:
            return int(value.strip())
        except ValueError:
            # try parsing integers represented in scientific notation
            frac, whole = math.modf(float(value.strip()))
            if frac == 0:
                return whole
            else:
                raise ParseError('invalid value for integer: %s' % value)

    def parse_float(self, value):
        return float(value.strip())


def annotate_with_aditional_chemical_identifiers(identifierconverter, compound):
    additional_identifiers = query_additional_chemical_identifiers(identifierconverter, compound['casn'])
    if additional_identifiers is None:
        return compound
    else:
        compound.update(additional_identifiers)
        return compound


def import_to_elastic(es, index, dirname, parser_schema, chemid_conversion_host, perform_chemid_conversion):
    parser = Parser(dirname, parser_schema)

    # Compounds
    compound_cache = {}
    logger.info('Parsing compounds from %s' % parser_schema['compounds']['file'])
    for compound in (compound for compound in parser.parse_compounds() if compound is not None):
        compound_cache[compound['code']] = compound
    logger.info('Indexing compounds in elasticsearch')
    bulk(es, ({
        '_index': index,
        '_type': 'compound',
        '_id': compound['chid'],
        '_source': compound
    } for compound in compound_cache.itervalues()))

    # Assays
    assay_cache = {}
    logger.info('Parsing assays from %s' % parser_schema['assays']['file'])
    for assay in (assay for assay in parser.parse_assays() if assay is not None):
        assay_cache[assay['assay_component_endpoint_name']] = assay
    logger.info('Indexing assays in elasticsearch')
    bulk(es, ({
        '_index': index,
        '_type': 'assay',
        '_id': assay['aeid'],
        '_source': assay
    } for assay in assay_cache.itervalues()))

    # Results - use compoud ID chid-aeid
    logger.info('Parsing and indexing results')
    bulk(es, ({
        '_index': index,
        '_type': 'result',
        '_id': '%s-%s' % (compound_cache[result['compound']]['chid'], assay_cache[result['assay']]['aeid']),
        '_source': {
            'compound': compound_cache[result['compound']],
            'assay': assay_cache[result['assay']],
            'result': result['result']
        }
    } for result in parser.parse_results()))


# -----------------------------------------------------------------------------
# Main

def main(argv=None):

    args = docopt(__doc__)

    elasticsearch_host = args.get('--elasticsearch-host', 'localhost')
    chemid_conversion_host = args.get('--chemid-conversion-host', 'localhost')
    perform_chemid_conversion = not args.get('--without-chemid-conversion', False)

    try:
        es = Elasticsearch(elasticsearch_host, timeout=30)
    except ElasticsearchException as e:
        print(e)
        sys.exit(2)

    if args['elastic'] and args['index'] and args['create']:
        elastic_index_create(es, args['<index>'], load_yaml_file(args['<index.yaml>']))

    elif args['elastic'] and args['index'] and args['drop']:
        elastic_index_delete(es, args['<index>'])

    elif args['elastic'] and args['index'] and args['exists']:
        if elastic_index_exists(es, args['<index>']):
            logger.info('Using existing Elastic index')
        else:
            logger.error('Elastic index does not exist')
            sys.exit(1)

    elif args['import']:
        import_to_elastic(
            es,
            args['<index>'],
            args['<dirname>'],
            load_yaml_file(args['<parser-schema.yaml>']),
            chemid_conversion_host,
            perform_chemid_conversion,
        )

        # Merge index
        logger.info('Merging index %s' % args['<index>'])
        es.indices.forcemerge(index=args['<index>'])

if __name__ == '__main__':
    main()

# -----------------------------------------------------------------------------