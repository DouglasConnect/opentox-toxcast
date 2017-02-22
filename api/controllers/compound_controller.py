from elasticsearch_dsl import Search
from controllers.client import client, INDEX
from controllers.helpers import (
    render, build_query, id_filter, search_query, term_filters,
    filtered_term_aggregation, build_global_aggs, offset_and_limit)


def compounds_get(offset=None,
                  limit=None,
                  query=None,
                  chidFilter=None,
                  clibFilter=None,
                  dssToxQCLevelFilter=None,
                  substanceTypeFilter=None) -> str:

    filters = (
        ('clib', clibFilter),
        ('dssToxQCLevel', dssToxQCLevelFilter),
        ('substanceType', substanceTypeFilter),
    )

    aggregations = {
        'clib': filtered_term_aggregation('Clib', 'clib.raw', 'clibFilter', chidFilter, query, filters),
        'dssToxQCLevel': filtered_term_aggregation('DSS Tox QC level', 'dssToxQCLevel.raw', 'dssToxQCLevelFilter', chidFilter, query, filters),
        'substanceType': filtered_term_aggregation('Substance type', 'substanceType.raw', 'substanceTypeFilter', chidFilter, query, filters),
    }

    search = Search(using=client, index=INDEX, doc_type='compound')
    search = search.query(build_query(id_filter(chidFilter), search_query(query), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'compounds')
