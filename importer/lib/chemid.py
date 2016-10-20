import re
import requests

import logging
logging.basicConfig(format='%(levelname)s %(message)s')
logging.getLogger('__main__').setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class ChemIdConversionError(Exception):
    pass


def chemical_identifiers_from_casnr(identifierconverter, casnr):
    if not re.match('^\d+-\d+-\d+$', casnr):
        logger.warn('Not a valid cas number: %s' % casnr)
        return None

    try:
        r = requests.get('http://%s/v1/cas/to/inchi' % identifierconverter, params={'cas': casnr})
        if r.status_code != 200 or r.json()['inchi'] is None:
            logger.warn('Could not convert cas number: %s' % casnr)
            return None
        inchi = r.json()['inchi']

        r = requests.get('http://%s/v1/inchi/to/inchikey' % identifierconverter, params={'inchi': inchi})
        if r.status_code != 200 or r.json()['inchikey'] is None:
            logger.warn('Could not convert to inchikey: %s' % inchi)
            return None
        inchikey = r.json()['inchikey']

        r = requests.get('http://%s/v1/inchi/to/smiles' % identifierconverter, params={'inchi': inchi})
        if r.status_code != 200 or r.json()['smiles'] is None:
            logger.warn('Could not convert to smiles: %s' % inchi)
            return None
        smiles = r.json()['smiles']

        result = {
            'casn': casnr,
            'inchi': inchi,
            'inchikey': inchikey,
            'smiles': smiles
        }

        logger.debug('Converted %(casn)s to inchi %(inchi)s, inchikey %(inchikey)s and smiles %(smiles)s' % result)
        return result

    except requests.exceptions.ConnectionError as e:
        raise ChemIdConversionError(e)
