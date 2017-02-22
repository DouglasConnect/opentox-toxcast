from elasticsearch_dsl import Search
from controllers.client import client, INDEX
from controllers.helpers import (
    render, build_query, id_filter, search_query, term_filters,
    filtered_term_aggregation, build_global_aggs, offset_and_limit)


def assays_get(offset=None,
               limit=None,
               query=None,
               aidFilter=None,
               aeidFilter=None,
               asidFilter=None,
               cellFormatFilter=None,
               detectionTechnologyTypeFilter=None,
               intendedTargetFamilyFilter=None,
               intendedTargetTypeFilter=None,
               organismFilter=None,
               technologicalTargetTypeFilter=None,
               timepointHrFilter=None,
               tissueFilter=None) -> str:

    filters = (
        ('aid', aidFilter),
        ('asid', asidFilter),
        ('cellFormat.raw', cellFormatFilter),
        ('detectionTechnologyType.raw', detectionTechnologyTypeFilter),
        ('intendedTargetFamily.raw', intendedTargetFamilyFilter),
        ('intendedTargetType.raw', intendedTargetTypeFilter),
        ('organism.raw', organismFilter),
        ('technologicalTargetType.raw', technologicalTargetTypeFilter),
        ('timepointHr', timepointHrFilter),
        ('tissue.raw', tissueFilter), )

    aggregations = {
        'cellFormat': filtered_term_aggregation('Cell Format', 'cellFormat.raw', 'cellFormatFilter', aeidFilter, query, filters),
        'detectionTechnologyType': filtered_term_aggregation('DSS Tox QC level', 'detectionTechnologyType.raw', 'detectionTechnologyTypeFilter', aeidFilter, query, filters),
        'intendedTargetFamily': filtered_term_aggregation('intended target family', 'intendedTargetFamily.raw', 'intendedTargetFamilyFilter', aeidFilter, query, filters),
        'intendedTargetType': filtered_term_aggregation('intended target type', 'intendedTargetType.raw', 'intendedTargetTypeFilter', aeidFilter, query, filters),
        'organism': filtered_term_aggregation('Organism', 'organism.raw', 'organismFilter', aeidFilter, query, filters),
        'technologicalTargetType': filtered_term_aggregation('technolgical target type', 'technologicalTargetType.raw', 'technologicalTargetTypeFilter', aeidFilter, query, filters),
        'timepointHr': filtered_term_aggregation('Timepoint Hr', 'timepointHr', 'timepointHrFilter', aeidFilter, query, filters),
        'tissue': filtered_term_aggregation('Tissue', 'tissue.raw', 'tissueFilter', aeidFilter, query, filters),
    }

    search = Search(using=client, index=INDEX, doc_type='assay')
    search = search.query(build_query(id_filter(aeidFilter), search_query(query), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'assays')
