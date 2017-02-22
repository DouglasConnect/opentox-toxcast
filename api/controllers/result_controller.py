from elasticsearch_dsl import Search
from elasticsearch_dsl.aggs import Filter
from controllers.client import client, INDEX
from controllers.helpers import (render, build_query, term_filters,
                                 term_aggregation, filtered_aggregation,
                                 build_global_aggs, offset_and_limit)


def results_get(offset=None,
                limit=None,
                chidFilter=None,
                clibFilter=None,
                dssToxQCLevelFilter=None,
                substanceTypeFilter=None,
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
                tissueFilter=None,
                hitcFilter=None) -> str:

    filters = (
        ('compound.chid', chidFilter),
        ('compound.clib', clibFilter),
        ('compound.dssToxQCLevel', dssToxQCLevelFilter),
        ('compound.substanceType', substanceTypeFilter),
        ('assay.aid', aidFilter),
        ('assay.asid', asidFilter),
        ('assay.aeid', aeidFilter),
        ('assay.cellFormat.raw', cellFormatFilter),
        ('assay.detectionTechnologyType.raw', detectionTechnologyTypeFilter),
        ('assay.intendedTargetFamily.raw', intendedTargetFamilyFilter),
        ('assay.intendedTargetType.raw', intendedTargetTypeFilter),
        ('assay.organism.raw', organismFilter),
        ('assay.technologicalTargetType.raw', technologicalTargetTypeFilter),
        ('assay.timepointHr', timepointHrFilter),
        ('assay.tissue.raw', tissueFilter),
        ('result.hitc', hitcFilter), )

    aggregations = {
        'compound.clib': {
            'name': 'Clib',
            'filterTerm': 'clibFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters, exclude='compound.clib'))),
                term_aggregation('compound.clib'))
        },
        'compound.dssToxQCLevel': {
            'name': 'DSS Tox QC level',
            'filterTerm': 'dssToxQCLevelFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters, exclude='compound.dssToxQCLevel'))),
                term_aggregation('compound.dssToxQCLevel'))
        },
        'compound.substanceType': {
            'name': 'Substance type',
            'filterTerm': 'substanceTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters, exclude='compound.substanceType'))),
                term_aggregation('compound.substanceType'))
        },
        'assay.cellFormat': {
            'name': 'Cell Format',
            'filterTerm': 'cellFormatFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters, exclude='assay.cellFormat.raw'))),
                term_aggregation('assay.cellFormat.raw'))
        },
        'assay.detectionTechnologyType': {
            'name': 'DSS Tox QC level',
            'filterTerm': 'detectionTechnologyTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters,
                            exclude='assay.detectionTechnologyType.raw'))),
                term_aggregation('assay.detectionTechnologyType.raw'))
        },
        'assay.intendedTargetFamily': {
            'name': 'intended target family',
            'filterTerm': 'intendedTargetFamilyFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters,
                            exclude='assay.intendedTargetFamily.raw'))),
                term_aggregation('assay.intendedTargetFamily.raw'))
        },
        'assay.intendedTargetType': {
            'name': 'intended target type',
            'filterTerm': 'intendedTargetTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters, exclude='assay.intendedTargetType.raw'))),
                term_aggregation('assay.intendedTargetType.raw'))
        },
        'assay.organism': {
            'name': 'Organism',
            'filterTerm': 'organismFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters, exclude='assay.organism.raw'))),
                term_aggregation('assay.organism.raw'))
        },
        'assay.technologicalTargetType': {
            'name': 'technolgical target type',
            'filterTerm': 'technologicalTargetTypeFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters,
                            exclude='assay.technologicalTargetType.raw'))),
                term_aggregation('assay.technologicalTargetType.raw'))
        },
        'assay.timepointHr': {
            'name': 'Timepoint Hr',
            'filterTerm': 'timepointHrFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters, exclude='assay.timepointHr'))),
                term_aggregation('assay.timepointHr'))
        },
        'assay.tissue': {
            'name': 'Tissue',
            'filterTerm': 'tissueFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(
                        term_filters(
                            filters, exclude='assay.tissue.raw'))),
                term_aggregation('assay.tissue.raw'))
        },
        'result.hitc': {
            'name': 'Hit call',
            'filterTerm': 'hitcFilter',
            'aggregation': filtered_aggregation(
                Filter(
                    build_query(term_filters(
                        filters, exclude='result.hitc'))),
                term_aggregation('result.hitc'))
        },
    }

    search = Search(using=client, index=INDEX, doc_type='result')
    search = search.query(build_query(term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations)
