from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import os
import string

elasticsearchhostname = os.getenv('ELASTICSEARCHHOSTNAME', 'elasticsearch')

client = Elasticsearch(elasticsearchhostname)

def result_es_to_toxcastapi(result):
    assay = {
        "assayId": result.assay.aeid, #RENAME happening here! assayId in result is aeid, AssayEndpointID
        #missing: aid
        #missing: acid
        #missing: asid
        "assaySourceName": result.assay.assay_source_name,
        "assaySourceLongName": result.assay.assay_source_long_name,
        "assaySourceDesc": result.assay.assay_source_desc,
        "assayName": result.assay.assay_name,
        "assayDesc": result.assay.assay_desc,
        "timepointHr": result.assay.timepoint_hr,
        "organismId": result.assay.organism_id,
        "organism": result.assay.organism,
        "tissue": result.assay.tissue,
        "cellFormat": result.assay.cell_format,
        "cellFreeComponentSource": result.assay.cell_free_component_source,
        "cellShortName": result.assay.cell_short_name,
        "cellGrowthMode": result.assay.cell_growth_mode,
        "assayFootprint": result.assay.assay_footprint,
        "assayFormatType": result.assay.assay_format_type,
        "assayFormatTypeSub": result.assay.assay_format_type_sub,
        "contentReadoutType": result.assay.content_readout_type,
        "dilutionSolvent": result.assay.dilution_solvent,
        "dilutionSolventPercentMax": result.assay.dilution_solvent_percent_max,
        "assayComponentName": result.assay.assay_component_name,
        "assayComponentDesc": result.assay.assay_component_desc,
        "assayComponentTargetDesc": result.assay.assay_component_target_desc,
        "parameterReadoutType": result.assay.assay_component_name,
        "assayDesignType": result.assay.assay_design_type,
        "assayDesignTypeSub": result.assay.assay_design_type_sub,
        "biologicalProcessTarget": result.assay.biological_process_target,
        "detectionTechnologyType": result.assay.detection_technology_type,
        "detectionTechnologyTypeSub": result.assay.detection_technology_type_sub,
        "detectionTechnology": result.assay.detection_technology,
        "signalDirectionType": result.assay.signal_direction_type,
        "keyAssayReagentType": result.assay.key_assay_reagent_type,
        "keyAssayReagent": result.assay.key_assay_reagent,
        "technologicalTargetType": result.assay.technological_target_type,
        "technologicalTargetTypeSub": result.assay.technological_target_type_sub,
        "assayEndpointName": result.assay.assay_component_endpoint_name,
        "assayEndpointDesc": result.assay.assay_component_endpoint_desc,
        "assayFunctionType": result.assay.assay_function_type,
        "normalizedDataType": result.assay.normalized_data_type,
        "analysisDirection": result.assay.analysis_direction,
        "burstAssay": result.assay.burst_assay == 1,
        "keyPositiveControl": result.assay.key_positive_control,
        "signalDirection": result.assay.signal_direction,
        "intendedTargetType": result.assay.intended_target_type,
        "intendedTargetTypeSub": result.assay.intended_target_type_sub,
        "intendedTargetFamily": result.assay.intended_target_family,
        "intendedTargetFamilySub": result.assay.intended_target_family_sub,
        "intendedTargetGeneId": splitString(result.assay.intended_target_gene_id, "|"),
        "intendedTargetEntrezGeneId": splitString(result.assay.intended_target_entrez_gene_id, "|"),
        "intendedTargetOfficialFullName": splitString(result.assay.intended_target_official_full_name, "|"),
        "intendedTargetGeneName": splitString(result.assay.intended_target_gene_name, "|"),
        "intendedTargetOfficialSymbol": splitString(result.assay.intended_target_official_symbol, "|"),
        "intendedTargetGeneSymbol": splitString(result.assay.intended_target_gene_symbol, "|"),
        "intendedTargetDescription": result.assay.intended_target_description,
        "intendedTargetUniprotAccessionNumber": result.assay.intended_target_uniprot_accession_number,
        "intendedTargetOrganismId": result.assay.intended_target_organism_id,
        "intendedTargetTrackStatus": result.assay.intended_target_track_status,
        "technologicalTargetGeneId": splitString(result.assay.technological_target_gene_id, "|"),
        "technologicalTargetEntrezGeneId": splitString(result.assay.technological_target_entrez_gene_id, "|"),
        "technologicalTargetOfficialFullName": splitString(result.assay.technological_target_official_full_name, "|"),
        "technologicalTargetGeneName": splitString(result.assay.technological_target_gene_name, "|"),
        "technologicalTargetOfficialSymbol": splitString(result.assay.technological_target_official_symbol, "|"),
        "technologicalTargetGeneSymbol": splitString(result.assay.technological_target_gene_symbol, "|"),
        "technologicalTargetDescription": result.assay.technological_target_description,
        "technologicalTargetUniprotAccessionNumber": result.assay.technological_target_uniprot_accession_number,
        "technologicalTargetOrganismId": result.assay.technological_target_organism_id,
        "technologicalTargetTrackStatus": result.assay.technological_target_track_status,
        "citationsCitationId": splitString(result.assay.citations_citation_id, "|"),
        "citationsPmid": splitString(result.assay.citations_pmid, "|"),
        "citationsDoi": splitString(result.assay.citations_doi, "|"),
        # missing: citations_other_source
        # missing: citations_other_id
        "citationsCitation": splitString(result.assay.citations_citation, "|"),
        "citationsTitle": splitString(result.assay.citations_title, "|"),
        "citationsAuthor": splitString(result.assay.citations_author, "|"),
        "citationsUrl": splitString(result.assay.citations_url, "|"),
        #missing: reagent_arid
        #missing: reagent_reagent_name_value
        #missing: reagent_reagent_name_value_type
        #missing: reagent_culture_or_assay
    }

    compound = {
        "compoundId": result.compound.chid,
        "chemicalName": result.compound.chnm,
        "casNumber": result.compound.casn,
        # "inchi": result.compound.inchi,
        # "inchiKey": result.compound.inchi_key,
        # "smiles": result.compound.smiles,
    }

    return_result = {
        "fitCategory": result.result.fitc,
        "hitcall": result.result.hitc,
        "level4Id": result.result.m4id,
        "log10ConcentrationMax": result.result.logc_max,
        "log10ConcentrationMin": result.result.logc_min,
        "maxMean": result.result.max_mean,
        "maxMedian": result.result.max_med,
        "ac10": result.result.modl_ac10,
        "acBaseline": result.result.modl_acb,
        "acCutoff": result.result.modl_acc,
        "gainAc50": result.result.modl_ga,
        "gainHillCoefficient": result.result.modl_gw,
        "lossAc50": result.result.modl_la,
        "lossHillCoefficient": result.result.modl_lw,
        "winningModel": result.result.modl,
        "rmse": result.result.modl_rmse,
        "oldstyleAc50": result.result.oldstyle_ac50,
        "oldstyleNegLogAc50": result.result.oldstyle_neg_log_ac50,
        "sampleId": result.result.spid,
        "zScore": result.result.zscore,
    }

    return {
        "assay": assay,
        "compound": compound,
        "result": return_result
    }

def results_get(assayIds, compounds=None, offset=None, limit=None) -> str:
    query = Search(using=client, index="toxcast") \
        .query('bool', filter=[Q('terms', **{'assay.aeid': assayIds})])
    offset = 0 if offset is None else offset
    limit = 10000 if limit is None else limit
    query = query[offset:limit]
    response = query.execute()
    if not response.success():
        return "Query was not successful", 500

    return list(map(result_es_to_toxcastapi, response))


def assays_assay_id_get(assayId) -> str:
    return 'do some magic!'


def assays_get(assayIds=None, offset=None, limit=None, facetOrganism=None, facetAssayName=None, facetTissue=None,
               facetCellFormat=None, facetAssayDesignType=None, facetFunction=None, facetIntendedTarget=None) -> str:
    query = Search(using=client, index="toxcast") \
        .filter(_type="assay")
    offset = 0 if offset is None else offset
    limit = 10000 if limit is None else limit
    query = query[offset:limit]
    response = query.execute()
    if not response.success():
        return "Query was not successful", 500

    return list(map(result_es_to_toxcastapi, response))


def compounds_compound_id_get(compoundId) -> str:
    return 'do some magic!'


def compounds_get(compoundIds=None, offset=None, limit=None) -> str:
    query = Search(using=client, index="toxcast") \
        .filter(_type="compound")
    offset = 0 if offset is None else offset
    limit = 10000 if limit is None else limit
    query = query[offset:limit]
    response = query.execute()
    if not response.success():
        return "Query was not successful", 500

    return list(map(result_es_to_toxcastapi, response))

def splitString(str, seperator):
    if (str):
        return str.split(seperator)
    else:
        return str
