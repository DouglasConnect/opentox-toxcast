import os
from elasticsearch import Elasticsearch

LIMIT = 10
INDEX = 'toxcast'
client = Elasticsearch(os.getenv('ELASTICSEARCHHOSTNAME', 'localhost'))
