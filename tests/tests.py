import logging
import os
logging.basicConfig(format='%(levelname)s %(message)s')
logging.getLogger('__main__').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

from bravado.client import SwaggerClient

logger.info('trying to get swagger definition')
client = SwaggerClient.from_url(os.getenv('SWAGGERURL', 'http://toxcast-api.cloud.douglasconnect.com/beta/swagger.json'))

logger.info('testing endpoints')
result = client.compound.compounds_get().result()
result = client.assay.assays_get().result()
result = client.result.results_get().result()
logger.info('all tests completed without exceptions')
