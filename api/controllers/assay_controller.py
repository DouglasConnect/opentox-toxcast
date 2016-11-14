from elasticsearch_dsl import Search, A
from elasticsearch_dsl.aggs import Filter
from controllers.helpers import *
from controllers.shared import *

def assays_get(offset = None, limit = None, aidFilter = None, aeidFilter = None, asidFilter = None) -> str:

    filters = (
        ('aid', aidFilter),
        ('asid', asidFilter),
        ('cellFormat', CellFormatFilter),
        ('detectionTechnologyType', DetectionTechnologyTypeFilter),
        ('intendedTargetFamily', IntendedTargetFamilyFilter),
        ('intendedTargetType', IntendedTargetTypeFilter),
        ('organism', OrganismFilter),
        ('technologicalTargetTypeSub', TechnologicalTargetTypeFilter),
        ('timepointHr', TimepointHrFilter),
        ('tissue', Tissue),
    )

    aggregations = {
        'cellFormat': {
            'name': 'Cell Format',
            'filterTerm': 'CellFormatFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='cellFormat'))),
                A('terms', field='cellFormat', min_doc_count=0))
        },
        'detectionTechnologyType': {
            'name': 'DSS Tox QC level',
            'filterTerm': 'DetectionTechnologyTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='detectionTechnologyType'))),
                A('terms', field='detectionTechnologyType', min_doc_count=0))
        },
        'intendedTargetFamily': {
            'name': 'intended target family type',
            'filterTerm': 'IntendedTargetFamilyFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='intendedTargetFamily'))),
                A('terms', field='intendedTargetFamily', min_doc_count=0))
        },
        'intendedTargetType': {
            'name': 'intended target type"',
            'filterTerm': 'IntendedTargetTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='intendedTargetType'))),
                A('terms', field='intendedTargetType', min_doc_count=0))
        },
        'organism': {
            'name': 'Organism',
            'filterTerm': 'OrganismFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='organism'))),
                A('terms', field='organism', min_doc_count=0))
        },
        'technologicalTargetTypeSub': {
            'name': 'technolgical target type',
            'filterTerm': 'TechnologicalTargetTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='technologicalTargetTypeSub'))),
                A('terms', field='technologicalTargetTypeSub', min_doc_count=0))
        },
        'timepointHr': {
            'name': 'Timepoint Hr',
            'filterTerm': 'TimepointHrFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='timepointHr'))),
                A('terms', field='timepointHr', min_doc_count=0))
        },
        'tissue': {
            'name': 'Tissue',
            'filterTerm': 'TissueFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='tissue'))),
                A('terms', field='tissue', min_doc_count=0))
        },
    }

    search = Search(using=client, index=INDEX, doc_type='assay')
    search = search.query(build_query(id_filter(aeidFilter), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'assays')
