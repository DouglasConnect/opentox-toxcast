# OpenTox • ToxCast

## API

To recreate the api after an upodate to the swagger definition, either copy the content of the swagger file in this directory into the [online swagger editor](http://editor.swagger.io/#/) and download a generated server api (python flask) or use the command line tool from the [swagger codegen page](https://github.com/swagger-api/swagger-codegen). The generated batch of files can then be dropped into ./api, but take care not to overwrite default_controllers.py which contains the code to serve the various endpoints (but incorporating changes if endpoints were modified).

Using swagger codegen:

    java -jar swagger-codegen-cli.jar generate -l python-flask -i Swagger.yaml -o api

or

    swagger-codegen generate -l python-flask -i Swagger.yaml -o api

## ToxCast data importer for Elasticsearch

ToxCast data importer is designed around ToxCast summary files releases where each ToxCast release has a separate parser and ElasticSearch mapping config files.

To see help on how to use the importer run (including Elasticsearch index management):

    ./importer/importer.py --help

Examples:

    ./importer/importer.py elastic index create toxcast importer/releases/2015-10-20/elastic-mapping.yaml

    ./importer/importer.py import toxcast /path/to/INVITRODB_V2_SUMMARY/ importer/releases/2015-10-20/parser-schema.yaml

    ./importer/importer.py elastic index drop toxcast

## Setup

Requirements:

- Elasticsearch 2.3
- Python 3
- Python requirements from requirements.txt

To install python requirements (preferably inside [pyvenv](https://virtualenv.pypa.io/en/stable/)) run:

    pip install -r requirements.txt --upgrade

## TODO

Old Swagger assay fields. Merge annotations with the new assay fields in the Swagger file:

    assayId:
      type: integer
      description: "Assay endpoint id"
    assaySourceName:
      type: string
      description: "a short name for the entity that conducted the assay"
    assaySourceLongName:
      type: string
      description: "the long name for the entity that conducted the assay"
    assaySourceDesc:
      type: string
      description: "Description of the organization that performed the assay"
    assayName:
      type: string
      description: "a short name for the assay, e.g. BSK_3C"
    assayDesc:
      type: string
      description: "Description of the assay"
    timepointHr:
      type: number
      description: "the duration length to conduct the test portion of the assay"
    organismId:
      type: integer
      description: "The NCBI Taxonomy id of the organism"
      x-ontology: http://purl.obolibrary.org/obo/OGG_0000000015
    organism:
      type: string
      description: "The target organism"
    tissue:
      type: string
      description: "the organ-level, anatomical entity of the protein or cell used in the assay"
    cellFormat:
      type: string
      description: "The target cell format"
    cellFreeComponentSource:
      type: string
      description: "the cellular or sample tissue source of the assayed gene protein"
    cellShortName:
      type: string
      description: "Cell short name"
    cellGrowthMode:
      type: string
      description: "Cell growth mode"
    assayFootprint:
      type: string
      description: "the physical format, such as plate density, in which an assay is performed"
    assayFormatType:
      type: string
      description: "the conceptual biological and/or chemical features of the assay system"
    assayFormatTypeSub:
      type: string
      description: "assay format subtype"
    contentReadoutType:
      type: string
      description: "the throughput and information content generated"
    dilutionSolvent:
      type: string
      description: "the solvent used as the negative control and to solubilize the test chemical"
    dilutionSolventPercentMax:
      type: number
      description: "the maximal amount of the dilution solvent tolerable for a particular assay"
    assayComponentName:
      type: string
      description: "a short name containing the assay and a component readout, e.g. BSK_3C_IL8"
    assayComponentDesc:
      type: string
      description: "assay component description"
    assayComponentTargetDesc:
      type: string
      description: "assay component target description"
    parameterReadoutType:
      type: string
      description: "parameter readout type"
    assayDesignType:
      type: string
      description: "assay design type"
    assayDesignTypeSub:
      type: string
      description: "assay design subtype"
    biologicalProcessTarget:
      type: string
      description: "biological process target"
    detectionTechnologyType:
      type: string
      description: "detection technology type"
    detectionTechnologyTypeSub:
      type: string
      description: "detection technology subtype"
    detectionTechnology:
      type: string
      description: "detection technology"
    signalDirectionType:
      type: string
      description: "signal direction type"
    keyAssayReagentType:
      type: string
      description: "key assay reagent type"
    keyAssayReagent:
      type: string
      description: "key assay reagent"
    technologicalTargetType:
      type: string
      description: "the measured chemical, molecular, cellular, or anatomical entity"
    technologicalTargetTypeSub:
      type: string
      description: "the measured chemical, molecular, cellular, or anatomical subtype"
    assayEndpointName:
      type: string
      description: "A short name containing the assay, the component readout, and an analysis applied, e.g. BSK_3C_IL8_up"
    assayEndpointDesc:
      type: string
      description: "Description of the assay endpoint"
    assayFunctionType:
      type: string
      description: "assay function type"
    normalizedDataType:
      type: string
      description: "normalized data type"
    analysisDirection:
      type: string
      description: "analysis direction (used values: positive/negative)"
    burstAssay:
      type: boolean
      description: "burst assay"
    keyPositiveControl:
      type: string
      description: "key positive control"
    signalDirection:
      type: string
      description: "signal direction (used values: loss/gain)"
    intendedTargetType:
      type: string
      description: "the objective chemical, molecular, cellular, pathway or anatomical entity"
    intendedTargetTypeSub:
      type: string
      description: "the objective chemical, molecular, cellular, pathway or anatomical entity"
    intendedTargetFamily:
      type: string
      description: "the target family of the objective target for the assay"
    intendedTargetFamilySub:
      type: string
      description: "the target family of the objective target for the assay"
    intendedTargetGeneId:
      type: array
      items:
        type: integer
      description: "List of target gene ids that are the objective "
    intendedTargetEntrezGeneId:
      type: array
      items:
        type: integer
      description: "List of target gene ids that are the objective (NCBI Entrez gene id)"
    intendedTargetOfficialFullName:
      type: array
      items:
        type: string
      description: "List of objective target offical full names"
    intendedTargetGeneName:
      type: array
      items:
        type: string
      description: "List of objective target gene names"
    intendedTargetOfficialSymbol:
      type: array
      items:
        type: string
      description: "List of objective target offical symbols"
    intendedTargetGeneSymbol:
      type: array
      items:
        type: string
      description: "List of objective target symbols"
    intendedTargetDescription:
      type: string
      description: "objective target description"
    intendedTargetUniprotAccessionNumber:
      type: string
      description: "objective target uniprot accesscion number"
    intendedTargetOrganismId:
      type: integer
      description: "intended target organism id"
    intendedTargetTrackStatus:
      type: string
      description: "objective target track status (used values: live)"
    technologicalTargetGeneId:
      type: array
      items:
        type: integer
      description: "measured molecular target gene id"
    technologicalTargetEntrezGeneId:
      type: array
      items:
        type: integer
      description: "List of measured molecular target gene ids (NCBI Entrez gene id)"
    technologicalTargetOfficialFullName:
      type: array
      items:
        type: string
      description: "List of measured molecular target offical full names"
    technologicalTargetGeneName:
      type: array
      items:
        type: string
      description: "List of technolmeasured molecularogical target gene names"
    technologicalTargetOfficialSymbol:
      type: array
      items:
        type: string
      description: "List of measured molecular target offical symbols"
    technologicalTargetGeneSymbol:
      type: array
      items:
        type: string
      description: "List of measured molecular target symbols"
    technologicalTargetDescription:
      type: string
      description: "measured molecular target description"
    technologicalTargetUniprotAccessionNumber:
      type: string
      description: "measured molecular target uniprot accesscion number"
    technologicalTargetOrganismId:
      type: integer
      description: "measured molecular target organism id"
    technologicalTargetTrackStatus:
      type: string
      description: "measured molecular target track status (used values: live)"
    citationsCitationId:
      type: array
      items:
        type: string
      description: "List of citation ids"
    citationsPmid:
      type: array
      items:
        type: string
      description: "List of PubMed citation ids"
    citationsDoi:
      type: array
      items:
        type: string
      description: "List of citation digital object identifiers"
    citationsCitation:
      type: array
      items:
        type: string
      description: "List of citation texts"
    citationsTitle:
      type: array
      items:
        type: string
      description: "List of citation titles"
    citationsAuthor:
      type: array
      items:
        type: string
      description: "List of citation authors"
    citationsUrl:
      type: array
      items:
        type: string
        format: url
      description: "List of citation urls"
