from elasticsearch_dsl import Search, A
from elasticsearch_dsl.aggs import Filter
from controllers.helpers import *
from controllers.shared import *

def assays_get(offset = None, limit = None, aidFilter = None, aeidFilter = None, asidFilter = None) -> str:

    filters = (
        ('aid', aidFilter),
        ('asid', asidFilter),
    )

    aggregations = {
    }

    search = Search(using=client, index=INDEX, doc_type='assay')
    search = search.query(build_query(id_filter(aeidFilter), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'assays')
