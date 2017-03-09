import yaml
import ruamel.yaml
yaml.load = lambda a: ruamel.yaml.load(a, ruamel.yaml.RoundTripLoader)
