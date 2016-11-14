from elasticsearch_dsl import Search, A
from elasticsearch_dsl.aggs import Filter
from controllers.helpers import *
from controllers.shared import *

def results_get(offset = None, limit = None, chidFilter = None, clibFilter = None, dssToxQCLevelFilter = None, substanceTypeFilter = None, aidFilter = None, aeidFilter = None, asidFilter = None, hitcFilter = None) -> str:

    filters = (
        ('compound.chid', chidFilter),
        ('compound.clib', clibFilter),
        ('compound.dssToxQCLevel', dssToxQCLevelFilter),
        ('compound.substanceType', substanceTypeFilter),

        ('assay.aeid', aeidFilter),
        ('assay.aid', aidFilter),
        ('assay.asid', asidFilter),

        ('result.hitc', hitcFilter),
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
            'filterTerm': 'substanceTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(term_filters(filters, exclude='substanceType'))),
                A('terms', field='compound.substanceType', min_doc_count=0))
        },
    }

    search = Search(using=client, index=INDEX, doc_type='result')
    search = search.query(build_query(term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations)
