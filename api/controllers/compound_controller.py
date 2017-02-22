from elasticsearch_dsl import Search
from elasticsearch_dsl.aggs import Filter
from controllers.client import client, INDEX
from controllers.helpers import (render, build_query, id_filter, term_filters,
                                 term_aggregation, filtered_aggregation,
                                 build_global_aggs, offset_and_limit)


def compounds_get(offset=None,
                  limit=None,
                  chidFilter=None,
                  clibFilter=None,
                  dssToxQCLevelFilter=None,
                  substanceTypeFilter=None) -> str:

    filters = (
        ('clib', clibFilter),
        ('dssToxQCLevel', dssToxQCLevelFilter),
        ('substanceType', substanceTypeFilter), )

    aggregations = {
        'clib': {
            'name': 'Clib',
            'filterTerm': 'clibFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(chidFilter),
                        term_filters(
                            filters, exclude='clib'))),
                term_aggregation('clib'))
        },
        'dssToxQCLevel': {
            'name': 'DSS Tox QC level',
            'filterTerm': 'dssToxQCLevelFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(chidFilter),
                        term_filters(
                            filters, exclude='dssToxQCLevel'))),
                term_aggregation('dssToxQCLevel'))
        },
        'substanceType': {
            'name': 'Substance type',
            'filterTerm': 'substanceTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(chidFilter),
                        term_filters(
                            filters, exclude='substanceType'))),
                term_aggregation('substanceType'))
        },
    }

    search = Search(using=client, index=INDEX, doc_type='compound')
    search = search.query(
        build_query(id_filter(chidFilter), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'compounds')
