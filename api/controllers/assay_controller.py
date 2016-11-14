from elasticsearch_dsl import Search
from elasticsearch_dsl.aggs import Filter
from controllers.client import client, INDEX
from controllers.helpers import (render, build_query, id_filter, term_filters,
                                 term_aggregation, filtered_aggregation,
                                 build_global_aggs, offset_and_limit)


def assays_get(offset=None,
               limit=None,
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
        'cellFormat': {
            'name': 'Cell Format',
            'filterTerm': 'cellFormatFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(aeidFilter),
                        term_filters(
                            filters, exclude='cellFormat.raw'))),
                term_aggregation('cellFormat.raw'))
        },
        'detectionTechnologyType': {
            'name': 'DSS Tox QC level',
            'filterTerm': 'detectionTechnologyTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(aeidFilter),
                        term_filters(
                            filters, exclude='detectionTechnologyType.raw'))),
                term_aggregation('detectionTechnologyType.raw'))
        },
        'intendedTargetFamily': {
            'name': 'Intended target family type',
            'filterTerm': 'intendedTargetFamilyFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(aeidFilter),
                        term_filters(
                            filters, exclude='intendedTargetFamily.raw'))),
                term_aggregation('intendedTargetFamily.raw'))
        },
        'intendedTargetType': {
            'name': 'Intended target type',
            'filterTerm': 'intendedTargetTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(aeidFilter),
                        term_filters(
                            filters, exclude='intendedTargetType.raw'))),
                term_aggregation('intendedTargetType.raw'))
        },
        'organism': {
            'name': 'Organism',
            'filterTerm': 'organismFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(aeidFilter),
                        term_filters(
                            filters, exclude='organism.raw'))),
                term_aggregation('organism.raw'))
        },
        'technologicalTargetType': {
            'name': 'Technolgical target type',
            'filterTerm': 'technologicalTargetTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(aeidFilter),
                        term_filters(
                            filters, exclude='technologicalTargetType.raw'))),
                term_aggregation('technologicalTargetType.raw'))
        },
        'timepointHr': {
            'name': 'Timepoint Hr',
            'filterTerm': 'timepointHrFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(aeidFilter),
                        term_filters(
                            filters, exclude='timepointHr'))),
                term_aggregation('timepointHr'))
        },
        'tissue': {
            'name': 'Tissue',
            'filterTerm': 'tissueFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        id_filter(aeidFilter),
                        term_filters(
                            filters, exclude='tissue.raw'))),
                term_aggregation('tissue.raw'))
        },
    }

    search = Search(using=client, index=INDEX, doc_type='assay')
    search = search.query(
        build_query(id_filter(aeidFilter), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'assays')
