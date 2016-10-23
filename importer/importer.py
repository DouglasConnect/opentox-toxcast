#!/usr/bin/env python3

'''
Usage:
    importer.py elastic index create <index> <index.yaml> [--elasticsearch-host=<hostname>] [--force]
    importer.py elastic index drop <index> [--elasticsearch-host=<hostname>]
    importer.py elastic index exists <index> [--elasticsearch-host=<hostname>]
    importer.py import <index> <dirname> <parser-schema.yaml> [--elasticsearch-host=<hostname>] [--chemid-conversion-host=<hostname>] [--perform-chemid-conversion]

Options:
  -h --help  Show this help.
  -e <hostname> --elasticsearch-host=<hostname>      Hostname of the elastic search host. Default is localhost.
  -i <hostname> --chemid-conversion-host=<hostname>  Hostname of the chemical identifier conversion tool (chemIdConvert). Default is localhost.
  --perform-chemid-conversion                        Perform chemical identifier conversion.
  --force                                            Force elasticsearch index creation even if index already exists.
'''

import os
import sys
import csv
import yaml
import codecs

import logging
logging.basicConfig(format='%(levelname)s %(message)s')
logging.getLogger('__main__').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

from docopt import docopt
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch, ElasticsearchException

from lib.parser import CSVParser, XLSParser
from lib.chemid import chemical_identifiers_from_casnr


# -----------------------------------------------------------------------------
# Utilities

def load_yaml_file(filename):
    with open(filename, 'r') as fi:
        return yaml.load(fi)


# -----------------------------------------------------------------------------
# Elastic index

def elastic_index_create(es, index, definition):
    es.indices.create(index=index, body=definition)


def elastic_index_delete(es, index, ignore=None):
    ignore = [] if ignore is None else ignore
    es.indices.delete(index=index, ignore=ignore)


def elastic_index_exists(es, index):
    return es.indices.exists(index=index)


# -----------------------------------------------------------------------------
# Data parsing and importing into Elastic

class ToxCastParser(object):

    def __init__(self, dirname, schema):
        self.dirname = dirname
        self.schema = schema

    def abspath(self, filename):
        return os.path.abspath(os.path.join(self.dirname, filename))

    def zip_fields(self, assay, fields, to_field, subfields):
        # zip list values from multiple fields and remove ones that have all resulting values None
        lists = [assay[f] for f in fields]
        values = [value for value in zip(*lists) if not all(v is None for v in value)]
        assay[to_field] = [dict(zip(subfields, v)) for v in values]
        for f in fields:
            del assay[f]

    def parse_compound_identifiers(self):
        return XLSParser(
            schema=self.schema['compoundIdentifiers']['properties'],
            encoding=self.schema['compoundIdentifiers'].get('encoding'),
            start_at_row=self.schema['compoundIdentifiers'].get('startAtRow')
        ).parse(self.abspath(self.schema['compoundIdentifiers']['file']))

    def parse_compounds(self):
        return CSVParser(
            schema=self.schema['compounds']['properties'],
            encoding=self.schema['compounds'].get('encoding'),
            start_at_row=self.schema['compounds'].get('startAtRow')
        ).parse(self.abspath(self.schema['compounds']['file']))

    def parse_assays(self):
        parser = CSVParser(
            schema=self.schema['assays']['properties'],
            encoding=self.schema['assays'].get('encoding'),
            start_at_row=self.schema['assays'].get('startAtRow'),
        )
        for assay in parser.parse(self.abspath(self.schema['assays']['file'])):
            self.zip_fields(
                assay,
                fields=('reagentArid', 'reagentReagentNameValue', 'reagentReagentNameValueType', 'reagentCultureOrAssay'),
                to_field='reagent',
                subfields=('arid', 'reagentNameValue', 'reagentNameValueType', 'cultureOrAssay'),
            )
            yield assay

    def parse_results(self):
        # get assays from the first results file (columns = assays)
        with codecs.open(self.abspath(self.schema['results'][0]['file']), 'rb', encoding=self.schema['results'][0].get('encoding', 'utf8')) as fi:
            for line in csv.reader(fi):
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
                line = [next(r) for r in result_parsers]
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


def annotate_with_aditional_chemical_identifiers(identifierconverter, compound):
    additional_identifiers = chemical_identifiers_from_casnr(identifierconverter, compound['casn'])
    if additional_identifiers is None:
        return compound
    else:
        compound.update(additional_identifiers)
        return compound


def import_to_elastic(es, index, dirname, parser_schema, chemid_conversion_host, perform_chemid_conversion):
    parser = ToxCastParser(dirname, parser_schema)

    # Compound identifiers
    compound_identifier_cache = {}
    logger.info('Parsing compound identifiers from %s' % parser_schema['compoundIdentifiers']['file'])
    for compound in (compound for compound in parser.parse_compound_identifiers() if compound is not None):
        compound_identifier_cache[compound['chid']] = compound

    # Compounds
    compound_cache = {}
    logger.info('Parsing compounds from %s' % parser_schema['compounds']['file'])
    for compound in (compound for compound in parser.parse_compounds() if compound is not None):
        if compound.get('chid') in compound_identifier_cache:
            compound.update(compound_identifier_cache[compound.get('chid')])
        else:
            # explicitly set identifier values to null for API consistency
            compound.update(dict([(k, None) for k in ('dssToxSubstanceId', 'dssToxStructureId', 'dssToxQCLevel', 'substanceType', 'substanceNote', 'structureSMILES', 'structureInChI', 'structureInChIKey', 'structureFormula', 'structureMolWt')]))
        compound_cache[compound['code']] = compound
    logger.info('Indexing compounds in elasticsearch')
    bulk(es, ({
        '_index': index,
        '_type': 'compound',
        '_id': compound['chid'],
        '_source': compound
    } for compound in compound_cache.values()))

    # Assays
    assay_cache = {}
    logger.info('Parsing assays from %s' % parser_schema['assays']['file'])
    for assay in (assay for assay in parser.parse_assays() if assay is not None):
        assay_cache[assay['assayComponentEndpointName']] = assay
    logger.info('Indexing assays in elasticsearch')
    bulk(es, ({
        '_index': index,
        '_type': 'assay',
        '_id': assay['aeid'],
        '_source': assay
    } for assay in assay_cache.values()))

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
    perform_chemid_conversion = args.get('--perform-chemid-conversion', False)

    try:
        es = Elasticsearch(elasticsearch_host, timeout=90)
    except ElasticsearchException as e:
        logger.error(e)
        sys.exit(2)

    if args['elastic'] and args['index'] and args['create']:
        if args['--force']:
            elastic_index_delete(es, args['<index>'], ignore=[400, 404])
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
