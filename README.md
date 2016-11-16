# OpenTox • ToxCast API

This repository contains the code for a REST Api to access the [EPA's ToxCast and Tox21](https://www.epa.gov/chemical-research/toxicity-forecaster-toxcasttm-data) data (currently the summary data release from October 2015), plus a data loader to import the official summary release data csv files into a data store. This API was developed by [Douglas Connect GmbH](http://www.douglasconnect.com) as part of the [OpenTox initiative](http://opentox.net/).

Douglas Connect runs a public version of this database at this URL (currently in Beta, so please be aware that things might still change):
http://toxcast-api.cloud.douglasconnect.com/ . At the root url you will find the Swagger UI interface that lets you explore the definitions of the endpoints, see the data schemata and try out the API.

This repository contains the [authorative OpenAPI/Swagger definition](Swagger.yaml) here at the root level, plus one subdirectory each for the [api implementation](api), the [importer](importer) that loads the csv files into Elasticsearch and the [tests](tests) that check if the api responses adhere to the OpenAPI definition.

## Why?

A [short presentation](http://slides.com/danielbachler/toxcast-api) from OpenTox Euro 2016 is available that explains the rationale for exposing the ToxCast data as an API.

## Guiding principles

Guiding principles for exposing the ToxCast data were:

* **Stay as true to the upstream data release as possible**. This means use column names in the official CSV files as field names for the objects we return even if these are sometimes a little cryptic.
* **Include aggregations (faceting) in the endpoints to enable data exploration**. This means that at the assays endpoint e.g. you will get several aggregations like a list of the available tissue types and a count of those given the other current filter terms.
* To harmonize data access accross other, similar data bases, a streamlined aproach is used of **one central endpoint, /results,** that returns all values of one assay and one compound at one particular point in time (to be exact, in the original ToxCast datasets this would be the values of one assay endpoint and one compound). At this endpoint, the results are returned as a list of structured objects that group the many fields into semantic concepts. In the case of ToxCast, this means that one result is an object with three fields: assay, compound and result. Assay contains all the metadata about the assay endpoint, compound the chemical names, official cas number, inchi etc, and result containing the AC50, hitcall etc values.
* Additionally to the /results endpoint, **the major logical entities should have their own endpoints**, in the case of ToxCast this means that there is a **/assays and /compounds** endpoint. All data included at these endpoints is also included at the /results endpoint, but exposed again here for easier browsing (e.g. to just quickly get a list of compounds contained in ToxCast).

## Overview of the code (aka how to run the api on your machine)

This section describes how the pieces fit together and how you can run your instance.

1. You need a running instance of Elasticsearch 2.x. It will be used to store the data and efficiently search/facet it.
2. Run the importer script, either the wrapping shell script importer/importer.sh or directly the python file. See instructions below for instructions. The importer script downloads the official October 2015 data release from the EPA website, extracts it, and parses the csv file into elasticsearch. This process typically takes around 4 hours.
3. Run the api, and access it locally at port 8080. What you are accessing is the python flask code generated via swagger-codegen from the OpenApi specification. The implementation we wrote takes care of passing the parameters to elasticsearch and returning the results.

## Using Docker/docker-compose

Each of the 3 main parts comes with it's own dockerfile to simplify it's use. There is also a docker-compose file here at the root level that makes it very easy to get started. All you need to do is install docker, clone this repository and run

    docker-compose up

Then wait until the importer is done.

## Using the importer or api without docker

See the Readme files in the subdirectories for instructions on how to run the parts without docker.
