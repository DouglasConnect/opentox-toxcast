# OpenTox • ToxCast API

This repository contains the code for a REST API to access the [EPA's ToxCast and Tox21](https://www.epa.gov/chemical-research/toxicity-forecaster-toxcasttm-data) data (currently the summary data release from October 2015), plus a data loader to import the official summary release data csv files into a data store. This API was developed by [Douglas Connect GmbH](http://www.douglasconnect.com) as part of the [OpenTox](http://opentox.net/) initiative.

Douglas Connect runs a public version of this database at this URL (currently in Beta, so please be aware that things might still change):
http://toxcast-api.cloud.douglasconnect.com/. At the root url you will find the Swagger UI interface that lets you explore the definitions of the endpoints, see the data schemata and try out the API.

This repository contains the authoritative [OpenAPI/Swagger definition](Swagger.yaml) here at the root level, plus one subdirectory each for the [api implementation](api), the [importer](importer) that loads the CSV files into [Elasticsearch](https://www.elastic.co/) and the [tests](tests) that check if the API responses adhere to the OpenAPI definition.


## Why?

A [short presentation](http://slides.com/danielbachler/toxcast-api) from OpenTox Euro 2016 is available that explains the rationale for exposing the ToxCast data as an API.


## Guiding principles

Guiding principles for exposing the ToxCast data were:

* **Stay as true to the upstream data release as possible**. This means use column names in the official CSV files as field names in the API and follow the structure as close as possible.
* **Provide means for easy data access and exploration**. This means that the API provides options for easy data filtering/searching and data aggregations (facets) that can drive the data exploration.


## API overview

ToxCast OpenTox provides the following endpoints:

* [`/assays`](http://toxcast-api.cloud.douglasconnect.com/beta/assays) provides information about assays (assay endpoints) used in ToxCast project,
* [`/compounds`](http://toxcast-api.cloud.douglasconnect.com/beta/compounds) provides information about compounds used in ToxCast project,
* [`/results`](http://toxcast-api.cloud.douglasconnect.com/beta/results) provides results of running
assays.

Results from all three endpoints have two parts: a list of data objects and a list of aggregations of fields in data objects for which aggregations make sense.

Data objects at the `/results` endpoint are composed not only of the actual results of assays but also complete information about the assay and the compound. While this might look a bit unusual it relieves you of the burden of making multiple API calls and connect those calls with IDs: you simply filter on the desired fields be it from assay, compound or the result and get all the information back in one call. Simple as that!

You can see how this comes together with using aggregations in this [example data explorer](http://opentox-data-explorer.cloud.douglasconnect.com/).

You can explore the API details here: http://toxcast-api.cloud.douglasconnect.com/beta/ui/


## Code overview (or how to run this on your machine)

This section describes how the pieces fit together and how you can run your instance.

1. You need a running instance of Elasticsearch 2.x. It will be used to store the data and efficiently search/facet it.
2. Run the importer script, either the wrapping shell script importer/importer.sh or directly the python file. See instructions below for instructions. The importer script downloads the official October 2015 data release from the EPA website, extracts it, and parses the CSV file into elasticsearch. This process typically takes around 3 hours.
3. Run the API, and access it locally at port 8080. What you are accessing is the python flask code generated via swagger-codegen from the OpenAPI specification. The implementation we wrote takes care of passing the parameters to Elasticsearch and returning the results.


## Using Docker and Docker Compose

Each of the 3 main parts comes with it's own dockerfile to simplify it's use. There is also a docker-compose file here at the root level that makes it very easy to get started. All you need to do is install docker, clone this repository and run

    docker-compose up

Then wait until the importer is done.


## Using the importer and API without Docker

See the README.md files in the subdirectories for instructions on how to run importer and API without docker.
