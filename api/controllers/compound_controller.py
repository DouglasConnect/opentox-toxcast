from elasticsearch_dsl import Search, A
from elasticsearch_dsl.aggs import Filter
from controllers.helpers import *
from controllers.shared import *


def compounds_get(offset = None, limit = None, chidFilter = None, clibFilter = None, dssToxQCLevelFilter = None, substanceTypeFilter = None) -> str:

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
            'filterTerm': 'substanceTypeFilter',
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
