import functools
import itertools

from elasticsearch_dsl import Q, A
from elasticsearch_dsl.aggs import Filter

RESULTS_LIMIT = 100
AGGREGATION_SIZE_LIMIT = 100


def render(response, aggregations, result_field_name='results'):
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
                }
                for key, agg in aggregations.items()
            }
        })
    return res


def build_query(*query_iterators):
    return functools.reduce(
        lambda a, b: a & b, itertools.chain(*query_iterators), Q())


def search_query(query=None):
    if query is not None:
        cleaned_query = query.strip()
        if cleaned_query:
            # yield Q('multi_match', query=cleaned_query, fields=['_all'], type='cross_fields', operator='and')
            wildcard_query = '+'.join([q + '*' for q in cleaned_query.split()])
            yield Q('simple_query_string', query=wildcard_query, fields=['_all'], flags='AND|PREFIX')


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
        terms = [
            x for x in terms
            if not isinstance(x, str) or (isinstance(x, str) and x.strip() != '')
        ]
        if len(terms):
            yield Q('terms', **{field: terms})


def offset_and_limit(query, offset=None, limit=None):
    offset = 0 if offset is None else offset
    limit = RESULTS_LIMIT if limit is None else limit
    return query[offset:limit + offset]


def term_aggregation(field, min_doc_count=0, size=AGGREGATION_SIZE_LIMIT):
    return A('terms', field=field, min_doc_count=min_doc_count, size=size)


def filtered_aggregation(flter, aggregation):
    flter.bucket('filtered', aggregation)
    return flter


def filtered_term_aggregation(name, field, filterTerm, idFilter, query, filters):
    return {
        'name': name,
        'filterTerm': filterTerm,
        'aggregation': filtered_aggregation(
            Filter(
                build_query(
                    id_filter(idFilter),
                    search_query(query),
                    term_filters(filters, exclude=field),
                )
            ),
            term_aggregation(field))
    }


def build_global_aggs(aggregations):
    aggs = A('global')
    for key, agg in aggregations.items():
        aggs.bucket(key, agg['aggregation'])
    return aggs
