import tablib


class Sniffer(object):

    def __init__(self, headers, report_filename=None, aggregation_term_limit=None):
        self.report_filename = report_filename
        self.aggregation_term_limit = aggregation_term_limit if aggregation_term_limit is not None else 50
        self.columns = dict([(h, Column(name=h, aggregation_term_limit=self.aggregation_term_limit)) for h in headers])

    def add_dict(self, data):
        for key, value in data.items():
            if isinstance(value, list):
                # process atomic values in lists
                for v in value:
                    if not isinstance(v, list) and not isinstance(v, dict):
                        self.columns[key].add_value(v)
            elif isinstance(value, dict):
                # ignore dict values
                pass
            else:
                self.columns[key].add_value(value)

    def report(self):
        data = tablib.Dataset(headers=['Name', 'Type', 'Aggregation'] + ['Term %d' % (i + 1) for i in range(self.aggregation_term_limit)])
        for i, col in enumerate(sorted(self.columns.values(), key=lambda a: (not a.is_aggregation_candidate(), a.name))):
            if col.aggregation_candidate:
                values = sorted(list(col.values)) + [None for i in range(self.aggregation_term_limit - len(col.values))]
            else:
                values = [None for i in range(self.aggregation_term_limit)]
            data.append([col.name, col.kind, col.is_aggregation_candidate()] + values)
        if self.report_filename:
            with open(self.report_filename, 'wb') as fo:
                fo.write(data.xls)
        else:
            print(data.csv)
            print()


class Column(object):

    def __init__(self, name, aggregation_term_limit):
        self.name = name
        self.aggregation_candidate = None
        self.aggregation_term_limit = aggregation_term_limit
        self.kind = None
        self.values = set()

    def is_aggregation_candidate(self):
        return self.aggregation_candidate if self.aggregation_candidate is True else False

    def add_value(self, value):
        if value is None or self.aggregation_candidate is False or value in self.values:
            pass
        else:
            # found new value
            if len(self.values) == self.aggregation_term_limit:
                self.aggregation_candidate = False
            else:
                self.values.add(value)
                self.aggregation_candidate = True
