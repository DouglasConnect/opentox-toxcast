import os
from elasticsearch import Elasticsearch

INDEX = 'toxcast'
client = Elasticsearch(os.getenv('ELASTICSEARCHHOSTNAME', 'localhost'))
