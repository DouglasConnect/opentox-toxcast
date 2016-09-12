from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import os

elasticsearchhostname = os.getenv('ELASTICSEARCHHOSTNAME', 'elasticsearch')

client = Elasticsearch(elasticsearchhostname)

def result_es_to_toxcastapi(result):
    smiles = ""
    inchi = ""
    inchikey = ""

    try:
        smiles = result.compound.smiles
    except AttributeError:
        pass
    try:
        inchi = result.compound.inchi
    except AttributeError:
        pass
    try:
        inchikey = result.compound.inchikey
    except AttributeError:
        pass

    return {
        "assayId": result.assay.aeid,
        "compoundId": result.compound.chid,
        "chemicalName": result.compound.chnm,
        "casNumber": result.compound.casn,
        "smiles": smiles,
        "inchi": inchi,
        "inchikey": inchikey,
        "hitcall": result.result.hitc
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
    return 'do some magic!'


def compounds_compound_id_get(compoundId) -> str:
    return 'do some magic!'


def compounds_get(compoundIds=None, offset=None, limit=None) -> str:
    return 'do some magic!'
