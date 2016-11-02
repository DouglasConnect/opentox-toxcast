import os
import functools
import itertools

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A
from elasticsearch_dsl.aggs import Filter

LIMIT = 10
INDEX = 'toxcast'
client = Elasticsearch(os.getenv('ELASTICSEARCHHOSTNAME', 'localhost'))


def compounds_get(offset=None, limit=None, compoundIds=None, clibFilter=None, dssToxQCLevelFilter=None, substanceTypeFilter=None) -> str:

    filters = (
        ('clib', clibFilter),
        ('dssToxQCLevel', dssToxQCLevelFilter),
        ('substanceType', substanceTypeFilter),
    )

    aggregations = {
        'clib': {
            'name': 'Clib',
            'filterTerm': 'clibFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(compoundIds), term_filters(filters, exclude='clib'))),
                A('terms', field='clib', min_doc_count=0))
        },
        'dssToxQCLevel': {
            'name': 'DSS Tox QC level',
            'filterTerm': 'dssToxQCLevelFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(compoundIds), term_filters(filters, exclude='dssToxQCLevel'))),
                A('terms', field='dssToxQCLevel', min_doc_count=0))
        },
        'substanceType': {
            'name': 'Substance type',
            'filterTerm': 'SubstanceTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(compoundIds), term_filters(filters, exclude='substanceType'))),
                A('terms', field='substanceType', min_doc_count=0))
        },
    }

    search = Search(using=client, index=INDEX, doc_type='compound')
    search = search.query(build_query(id_filter(compoundIds), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'compounds')


def assays_get(offset=None, limit=None, assayEndpointIds=None, assayIds=None, studyIds=None) -> str:

    filters = (
        ('aid', assayIds),
        ('asid', studyIds),
    )

    aggregations = {
    }

    search = Search(using=client, index=INDEX, doc_type='assay')
    search = search.query(build_query(id_filter(assayEndpointIds), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'assays')


def results_get(offset=None, limit=None, compoundIds=None, clibFilter=None, dssToxQCLevelFilter=None, substanceTypeFilter=None, assayIds=None, assayEndpointIds=None, studyIds=None) -> str:

    filters = (
        ('compound.chid', compoundIds),
        ('compound.clib', clibFilter),
        ('compound.dssToxQCLevel', dssToxQCLevelFilter),
        ('compound.substanceType', substanceTypeFilter),

        ('assay.aeid', assayEndpointIds),
        ('assay.aid', assayIds),
        ('assay.asid', studyIds),
    )

    aggregations = {
        'compound.clib': {
            'name': 'Clib',
            'filterTerm': 'clibFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(term_filters(filters, exclude='clib'))),
                A('terms', field='compound.clib', min_doc_count=0))
        },
        'compound.dssToxQCLevel': {
            'name': 'DSS Tox QC level',
            'filterTerm': 'dssToxQCLevelFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(term_filters(filters, exclude='dssToxQCLevel'))),
                A('terms', field='compound.dssToxQCLevel', min_doc_count=0))
        },
        'compound.substanceType': {
            'name': 'Substance type',
            'filterTerm': 'SubstanceTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(term_filters(filters, exclude='substanceType'))),
                A('terms', field='compound.substanceType', min_doc_count=0))
        },
    }

    search = Search(using=client, index=INDEX, doc_type='result')
    search = search.query(build_query(id_filter(compoundIds), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations)


# -----------------------------------------------------------------------------
# Helpers

def render(response, aggregations, result_field_name = 'results'):
    if not response.success():
        return 'Query was not successful', 500
    res = {
        'total': response.hits.total,
        result_field_name: [hit.to_dict() for hit in response]
    }
    if hasattr(response, 'aggregations'):
        values = response.aggregations.to_dict()['global']
        res.update({
            'aggregations': {
                key: {
                    'name': agg['name'],
                    'filterTerm': agg['filterTerm'],
                    'buckets': values[key]['filtered']['buckets']
                } for key, agg in aggregations.items()}
        })
    return res


def build_query(*query_iterators):
    return functools.reduce(lambda a, b: a & b, itertools.chain(*query_iterators), Q())


def id_filter(ids):
    if ids is not None:
        ids = [x.strip() for x in ids if x.strip() != '']
        if len(ids):
            yield Q('ids', values=ids)


def term_filters(filters, exclude=None):
    for field, terms in filters:
        if field != exclude:
            yield from term_filter(field, terms)


def term_filter(field, terms):
    if terms is not None:
        terms = [x for x in terms if x.strip() != '']
        if len(terms):
            yield Q('terms', **{field: terms})


def offset_and_limit(query, offset=None, limit=None):
    offset = 0 if offset is None else offset
    limit = LIMIT if limit is None else limit
    return query[offset:limit+offset]


def filtered_aggregation(flter, aggregation):
    flter.bucket('filtered', aggregation)
    return flter


def build_global_aggs(aggregations):
    aggs = A('global')
    for key, agg in aggregations.items():
        aggs.bucket(key, agg['aggregation'])
    return aggs

# -----------------------------------------------------------------------------
