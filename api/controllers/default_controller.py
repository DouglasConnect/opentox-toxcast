import os
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A

INDEX = 'toxcast'
client = Elasticsearch(os.getenv('ELASTICSEARCHHOSTNAME', 'localhost'))

def assays_get(offset = None, limit = None, assayIds = None, assayEndpointIds = None, studyIds = None) -> str:
    filters = (
        ('studyId', studyIds),
        ('assayEndpointId', assayEndpointIds),
    )
    # aggregations = (
    #     ('species', A('terms', field='species.raw', min_doc_count=0)),
    #     ('entryStatus', A('terms', field='entryStatus.raw', min_doc_count=0)),
    #     ('usabilityDesc', A('terms', field='usabilityDesc.raw', min_doc_count=0)),
    #     ('guidelineName', A('terms', field='guidelineName.raw', min_doc_count=0)),
    #     ('adminMethod', A('terms', field='adminMethod.raw', min_doc_count=0)),
    #     ('adminRoute', A('terms', field='adminRoute.raw', min_doc_count=0)),
    #     ('studyType', A('terms', field='studyType.raw', min_doc_count=0)),
    #     ('effectCategory', A('terms', field='effectCategory.raw', min_doc_count=0)),
    # )
    query = Search(using=client, index=INDEX, doc_type='assay')
    query = filter_by_ids(query, assayIds)
    query = filter_by_filters(query, filters)
    query = filter_by_offset_and_limit(query, offset, limit)
    # add_aggregations(query, aggregations)
    return render(query.execute())

def compounds_get(offset = None, limit = None, compoundIds = None, dssToxQCLevelFilter = None, substanceTypeFilter = None) -> str:
    query = Search(using=client, index=INDEX, doc_type='compound')
    query = filter_by_ids(query, compoundIds)
    query = filter_by_offset_and_limit(query, offset, limit)
    return render(query.execute())

def results_get(offset = None, limit = None, compoundIds = None, clibFilter = None, dssToxQCLevelFilter = None, substanceTypeFilter = None, assayIds = None, assayEndpointIds = None, studyIds = None) -> str:
    filters = (
        ('compound.chid', compoundIds),
        ('compound.clib', clibFilter),
        ('compound.dssToxQCLevel', dssToxQCLevelFilter),
        ('compound.substanceType', substanceTypeFilter),
        ('assay.assayId', assayIds),
        ('assay.studyId', studyIds),
        ('assay.assayEndpointId', assayEndpointIds),
    )
    aggregations = (
        ('clib', A('terms', field='compound.clib', min_doc_count=0)),
        ('dssToxQLevel', A('terms', field='compound.dssToxQCLevel', min_doc_count=0)),
        ('substanceType', A('terms', field='compound.substanceType', min_doc_count=0)),
    )
    query = Search(using=client, index=INDEX, doc_type='result')
    query = filter_by_filters(query, filters)
    query = filter_by_offset_and_limit(query, offset, limit)
    add_aggregations(query, aggregations)
    return render(query.execute())

def render(response):
    if not response.success():
        return 'Query was not successful', 500
    res = {
        'total': response.hits.total,
        'results': [dict(hit.to_dict(), _API_ID_=hit.meta.id) for hit in response]
    }
    if hasattr(response, 'aggregations'):
        res.update({'aggregations': dict([(k, {'filterTerm': k + 'Filter', 'buckets': v['buckets']}) for k, v in response.aggregations.to_dict().items()])})
    return res


def filter_by_ids(query, ids):
    if ids:
        ids = [x for x in ids if x.strip() != '']
        if ids:
            return query.filter('ids', values=ids)
    else:
        return query


def filter_by_terms(query, field, terms):
    if terms:
        terms = [x for x in terms if x.strip() != '']
        if terms:
            return query.filter('terms', **{field: terms})
    else:
        return query


def filter_by_filters(query, filters):
    for f in filters:
        query = filter_by_terms(query, f[0], f[1])
    return query


def filter_by_offset_and_limit(query, offset=None, limit=None):
    offset = 0 if offset is None else offset
    limit = 100 if limit is None else limit
    return query[offset:limit+offset]


def add_aggregations(query, aggregations):
    for a in aggregations:
        query.aggs.bucket(a[0], a[1])
