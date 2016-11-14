from elasticsearch_dsl import Search, A
from elasticsearch_dsl.aggs import Filter
from controllers.helpers import *
from controllers.shared import *

def results_get(offset = None, limit = None, chidFilter = None, clibFilter = None, dssToxQCLevelFilter = None, substanceTypeFilter = None, aidFilter = None, aeidFilter = None, asidFilter = None, cellFormatFilter = None, detectionTechnologyTypeFilter = None, intendedTargetFamilyFilter = None, intendedTargetTypeFilter = None, organismFilter = None, technologicalTargetTypeFilter = None, timepointHrFilter = None, tissueFilter = None, hitcFilter = None) -> str:

    filters = (
        ('compound.chid', chidFilter),
        ('compound.clib', clibFilter),
        ('compound.dssToxQCLevel', dssToxQCLevelFilter),
        ('compound.substanceType', substanceTypeFilter),

        ('assay.aeid', aeidFilter),
        ('assay.aid', aidFilter),
        ('assay.asid', asidFilter),
        ('assay.cellFormat', cellFormatFilter),
        ('assay.detectionTechnologyType', detectionTechnologyTypeFilter),
        ('assay.intendedTargetFamily', intendedTargetFamilyFilter),
        ('assay.intendedTargetType', intendedTargetTypeFilter),
        ('assay.organism', organismFilter),
        ('assay.technologicalTargetType', technologicalTargetTypeFilter),
        #('assay.timepointHr', timepointHrFilter),
        ('assay.tissue', tissueFilter),

        #('result.hitc', hitcFilter),
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
        'assay.cellFormat': {
            'name': 'Cell Format',
            'filterTerm': 'CellFormatFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='cellFormat'))),
                A('terms', field='assay.cellFormat', min_doc_count=0))
        },
        'assay.detectionTechnologyType': {
            'name': 'DSS Tox QC level',
            'filterTerm': 'DetectionTechnologyTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='detectionTechnologyType'))),
                A('terms', field='assay.detectionTechnologyType', min_doc_count=0))
        },
        'assay.intendedTargetFamily': {
            'name': 'intended target family type',
            'filterTerm': 'IntendedTargetFamilyFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='intendedTargetFamily'))),
                A('terms', field='assay.intendedTargetFamily', min_doc_count=0))
        },
        'assay.intendedTargetType': {
            'name': 'intended target type"',
            'filterTerm': 'IntendedTargetTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='intendedTargetType'))),
                A('terms', field='assay.intendedTargetType', min_doc_count=0))
        },
        'assay.organism': {
            'name': 'Organism',
            'filterTerm': 'OrganismFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='organism'))),
                A('terms', field='assay.organism', min_doc_count=0))
        },
        'assay.technologicalTargetType': {
            'name': 'technolgical target type',
            'filterTerm': 'TechnologicalTargetTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='technologicalTargetType'))),
                A('terms', field='assay.technologicalTargetType', min_doc_count=0))
        },
        # 'assay.timepointHr': {
        #     'name': 'Timepoint Hr',
        #     'filterTerm': 'TimepointHrFilter',
        #     'aggregation': filtered_aggregation(
        #         Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='timepointHr'))),
        #         A('terms', field='assay.timepointHr', min_doc_count=0))
        # },
        'assay.tissue': {
            'name': 'Tissue',
            'filterTerm': 'TissueFilter',
            'aggregation': filtered_aggregation(
                Filter(build_query(id_filter(aeidFilter), term_filters(filters, exclude='tissue'))),
                A('terms', field='assay.tissue', min_doc_count=0))
        },
        # 'result.hitc': {
        #     'name': 'Hit call',
        #     'filterTerm': 'hitcFilter',
        #     'aggregation': filtered_aggregation(
        #         Filter(build_query(term_filters(filters, exclude='hitc'))),
        #         A('terms', field='result.hitc', min_doc_count=0))
        # },
    }

    search = Search(using=client, index=INDEX, doc_type='result')
    search = search.query(build_query(term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations)
