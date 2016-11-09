#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

ELASTICSEARCHHOSTNAME="${ELASTICSEARCHHOSTNAME:-elasticsearch}"
IDENTIFIERCONVERTERHOSTNAME="${IDENTIFIERCONVERTERHOSTNAME:-chemidconvert}"
IDENTIFIERCONVERTERPORT="${IDENTIFIERCONVERTERPORT:-8080}"
# The data we need from the offical Toxcast release the official summary data relase from
# ftp://newftp.epa.gov/comptox/High_Throughput_Screening_Data/Summary_Files/INVITRODB_V2_SUMMARY.zip
# We use a mirror in europe for faster downloading:
TOXCASTDATAURL="${TOXCASTDATAURL:-https://storage.googleapis.com/douglasconnect-public/data/toxcast/INVITRODB_V2_SUMMARY.zip}"
TOXCASTCOMPOUNDSURL="${TOXCASTCOMPOUNDSURL:-https://storage.googleapis.com/douglasconnect-public/data/toxcast/DSSTox_ToxCastRelease_20151019.zip}"

echo "starting toxcast data import"
echo "importing into elasticsearch at $ELASTICSEARCHHOSTNAME"
echo "using identifierconverter at $IDENTIFIERCONVERTERHOSTNAME:$IDENTIFIERCONVERTERPORT"

# echo "sleeping now to give EL some time if run as part of docker-compose"
sleep 10
#
# echo "Trying to ping elasticsearch"
# if ! ping -c 1 $ELASTICSEARCHHOSTNAME &> /dev/null
# then
#   echo "Could not reach elasticsearch at $ELASTICSEARCHHOSTNAME"
#   exit 2
# fi
# echo "pinging elasticsearch worked"
#
# echo "Trying to ping chemidconvert service"
# if ! ping -c 1 $IDENTIFIERCONVERTERHOSTNAME &> /dev/null
# then
#   echo "Could not reach chemidconvert at $IDENTIFIERCONVERTERHOSTNAME"
#   exit 2
# fi
# echo "pinging chemidconvert worked"

if python /code/importer.py elastic index exists toxcast --elasticsearch-host $ELASTICSEARCHHOSTNAME
then
  if [ -z "$DROPEXISTINGINDEX" ]; then
    echo "Deleting existing index toxcast"
    python /code/importer.py elastic index drop toxcast --elasticsearch-host $ELASTICSEARCHHOSTNAME
    echo "Index deleted"
  else
    echo "Elasticsearch already contains an toxcast index, aborting data import"#
    exit 1
  fi
fi

echo "Elasticsearch does not contain the toxcast document yet, downloading data from $TOXCASTDATAURL"

if [ ! -d /data/INVITRODB_V2_SUMMARY ]
then
  if [ ! -e /data/INVITRODB_V2_SUMMARY.zip ]
  then
    if [ ! -d /data ]
    then
      mkdir /data
      mkdir /data/DSSTox_ToxCastRelease_20151019
    fi

    curl -o /data/INVITRODB_V2_SUMMARY.zip $TOXCASTDATAURL
    echo "toxcast data downloaded, unzipping"
  else
    echo "toxcast download already existed"
  fi

  if [ ! -e /data/DSSTox_ToxCastRelease_20151019.zip ]
  then
    curl -o /data/DSSTox_ToxCastRelease_20151019/DSSTox_ToxCastRelease_20151019.zip $TOXCASTCOMPOUNDSURL
    echo "toxcast compounds downloaded, unzipping"
  else
    echo "toxcast compounds already existed"
  fi

  echo "/data/INVITRODB_V2_SUMMARY did not exist, extracting data now"
  cd /data
  unzip /data/INVITRODB_V2_SUMMARY.zip
  echo "toxcast data unzipped"
  cd /data/DSSTox_ToxCastRelease_20151019
  unzip /data/DSSTox_ToxCastRelease_20151019/DSSTox_ToxCastRelease_20151019.zip
  echo "toxcast compounds unzipped"
  rm /data/INVITRODB_V2_SUMMARY.zip
  rm /data/DSSTox_ToxCastRelease_20151019/DSSTox_ToxCastRelease_20151019.zip
else
  echo "toxcast was already unzipped"
fi

echo "Creating elasticsearch index"
python /code/importer.py elastic index create toxcast /code/releases/2015-10-20/elastic-mapping.yaml --elasticsearch-host $ELASTICSEARCHHOSTNAME
echo "ingesting toxcast data now"
python /code/importer.py import toxcast /data /code/releases/2015-10-20/parser-schema.yaml --elasticsearch-host $ELASTICSEARCHHOSTNAME --chemid-conversion-host "$IDENTIFIERCONVERTERHOSTNAME:$IDENTIFIERCONVERTERPORT"

echo "Finished importing toxcast data!"
