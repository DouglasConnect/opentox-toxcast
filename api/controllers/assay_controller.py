from elasticsearch_dsl import Search, A
from elasticsearch_dsl.aggs import Filter
from controllers.helpers import *
from controllers.shared import *

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
