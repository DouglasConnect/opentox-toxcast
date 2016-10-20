import csv
import xlrd
import math
import codecs

import logging
logging.basicConfig(format='%(levelname)s %(message)s')
logging.getLogger('__main__').setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class ParseError(Exception):
    pass


class Parser(object):

    def __init__(self, schema, encoding=None, start_at_row=None):
        self.schema = schema
        self.encoding = encoding if encoding is not None else 'utf8'
        self.start_at_row = start_at_row if start_at_row is not None else 0

    def parse_value(self, schema, line):
        value = line[schema['col']]
        nulls = schema.get('nulls')

        if nulls is not None and value in nulls:
            return None

        if schema['type'] == 'string':
            return self.parse_string(value)
        elif schema['type'] == 'boolean':
            return self.parse_boolean(value)
        elif schema['type'] == 'integer':
            return self.parse_integer(value)
        elif schema['type'] == 'float':
            return self.parse_float(value)
        else:
            raise ParseError('unknown property type: \'%s\'' % schema['type'])

    def parse_string(self, value):
        return value.strip()

    def parse_boolean(self, value):
        if int(value.strip()) in [0, 1]:
            return bool(int(value.strip()))
        else:
            raise ParseError('invalid value for bool: %s' % value)

    def parse_integer(self, value):
        try:
            return int(value.strip())
        except ValueError:
            # try parsing integers represented in scientific notation
            frac, whole = math.modf(float(value.strip()))
            if frac == 0:
                return whole
            else:
                raise ParseError('invalid value for integer: %s' % value)

    def parse_float(self, value):
        return float(value.strip())


class CSVParser(Parser):

    def parse(self, filename):
        with codecs.open(filename, 'r', encoding=self.encoding) as fi:
            for i, line in enumerate(csv.reader(fi)):
                if i >= self.start_at_row:
                    yield(self.parse_line(filename, i, line))

    def parse_line(self, filename, i, line):
        try:
            return dict([(key, self.parse_value(schema, line)) for key, schema in self.schema.items()])
        except Exception as e:
            logger.warn('Error parsing file %s at line %s: %s' % (filename, i, e))
            return None


class XLSParser(Parser):

    def parse(self, filename):
        book = xlrd.open_workbook(filename)
        sheet = book.sheet_by_index(0)
        for rx in range(sheet.nrows):
            if rx >= self.start_at_row:
                yield(self.parse_line(filename, rx, sheet.row(rx)))

    def parse_line(self, filename, rx, line):
        try:
            return dict([(key, self.parse_value(schema, [str(c.value) for c in line])) for key, schema in self.schema.items()])
        except Exception as e:
            logger.warn('Error parsing file %s at line %s: %s' % (filename, rx, e))
            return None
