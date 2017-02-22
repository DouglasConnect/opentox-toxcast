from elasticsearch_dsl import Search
from controllers.client import client, INDEX
from controllers.helpers import (
    render, build_query, id_filter, search_query, term_filters,
    filtered_term_aggregation, build_global_aggs, offset_and_limit)


def results_get(offset=None,
                limit=None,
                query=None,
                resultIdFilter=None,
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
        ('result.hitc', hitcFilter),
    )

    aggregations = {
        'compound.clib': filtered_term_aggregation('Clib', 'compound.clib', 'clibFilter', resultIdFilter, query, filters),
        'compound.dssToxQCLevel': filtered_term_aggregation('DSS Tox QC level', 'compound.dssToxQCLevel', 'dssToxQCLevelFilter', resultIdFilter, query, filters),
        'compound.substanceType': filtered_term_aggregation('Substance type', 'compound.substanceType', 'substanceTypeFilter', resultIdFilter, query, filters),
        'assay.cellFormat': filtered_term_aggregation('Cell Format', 'assay.cellFormat.raw', 'cellFormatFilter', resultIdFilter, query, filters),
        'assay.detectionTechnologyType': filtered_term_aggregation('DSS Tox QC level', 'assay.detectionTechnologyType.raw', 'detectionTechnologyTypeFilter', resultIdFilter, query, filters),
        'assay.intendedTargetFamily': filtered_term_aggregation('intended target family', 'assay.intendedTargetFamily.raw', 'intendedTargetFamilyFilter', resultIdFilter, query, filters),
        'assay.intendedTargetType': filtered_term_aggregation('intended target type', 'assay.intendedTargetType.raw', 'intendedTargetTypeFilter', resultIdFilter, query, filters),
        'assay.organism': filtered_term_aggregation('Organism', 'assay.organism.raw', 'organismFilter', resultIdFilter, query, filters),
        'assay.technologicalTargetType': filtered_term_aggregation('technolgical target type', 'assay.technologicalTargetType.raw', 'technologicalTargetTypeFilter', resultIdFilter, query, filters),
        'assay.timepointHr': filtered_term_aggregation('Timepoint Hr', 'assay.timepointHr', 'timepointHrFilter', resultIdFilter, query, filters),
        'assay.tissue': filtered_term_aggregation('Tissue', 'assay.tissue.raw', 'tissueFilter', resultIdFilter, query, filters),
        'result.hitc': filtered_term_aggregation('Hit call', 'result.hitc', 'hitcFilter', resultIdFilter, query, filters),
    }

    search = Search(using=client, index=INDEX, doc_type='result')
    search = search.query(build_query(id_filter(resultIdFilter), search_query(query), term_filters(filters)))
    search = offset_and_limit(search, offset, limit)
    search.aggs.bucket('global', build_global_aggs(aggregations))

    return render(search.execute(), aggregations, 'results')
