#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

ELASTICSEARCHHOSTNAME="${ELASTICSEARCHHOSTNAME:-elasticsearch}"
IDENTIFIERCONVERTERHOSTNAME="${IDENTIFIERCONVERTERHOSTNAME:-chemidconvert}"
IDENTIFIERCONVERTERPORT="${IDENTIFIERCONVERTERPORT:-8080}"
# The data we need from the offical Toxcast release is split into two zip files, so we are using a repackaged zip file below.
# The original data consists of the assay data files from this file:
# ftp://newftp.epa.gov/comptox/High_Throughput_Screening_Data/ToxCast_Data_Oct_2015/INVITRODB_V2_LEVEL5.zip
# plus the assay and compound summary files from this file:
# ftp://newftp.epa.gov/comptox/High_Throughput_Screening_Data/Summary_Files/INVITRODB_V2_SUMMARY.zip
TOXCASTDATAURL="${TOXCASTDATAURL:-https://storage.googleapis.com/douglasconnect-public/data/toxcast/toxcast.zip}"

echo "starting toxcast data import"
echo "importing into elasticsearch at $ELASTICSEARCHHOSTNAME"
echo "using identifierconverter at $IDENTIFIERCONVERTERHOSTNAME:$IDENTIFIERCONVERTERPORT"

# echo "sleeping now to give EL some time if run as part of docker-compose"
# sleep 10
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

if python /code/toolbox.py elastic index exists toxcast --elasticsearchhost $ELASTICSEARCHHOSTNAME
then
  echo "Elasitsearch already contains a document called toxcast, aborting data loading"#
  exit 1
fi

echo "Elasticsearch does not contain the toxcast document yet, downloading data from $TOXCASTDATAURL"

if [ ! -e /data/toxcast.zip ]
then
  if [ ! -d /data ]
  then
    mkdir /data
  fi

  curl -o /data/toxcast.zip $TOXCASTDATAURL
  echo "toxcast data downloaded, unzipping"
else
  echo "toxcast download already existed"
fi

if [ ! -d /data/csv ]
then
  echo "/data/toxcast.zip did not exist, downloading data now"
  cd /data
  unzip /data/toxcast.zip
  echo "toxcast data unzipped"
  rm /data/toxcast.zip
else
  echo "toxcast was already unzipped"
fi


DATAFILES=""

for file in /data/csv/results/*.csv
do
  DATAFILES+="$file "
done

echo "ingesting the following files now: $DATAFILES"

python /code/toolbox.py elastic index create toxcast /code/elastic/index.yaml --elasticsearchhost $ELASTICSEARCHHOSTNAME
python /code/toolbox.py elastic data load toxcast /code/elastic/parser-schema.yaml /data/csv/Assay_Summary_151020.csv /data/csv/Chemical_Summary_151020.csv $DATAFILES --elasticsearchhost $ELASTICSEARCHHOSTNAME --identifierconverter "$IDENTIFIERCONVERTERHOSTNAME:$IDENTIFIERCONVERTERPORT"

echo "Finished importing toxcast data!"
