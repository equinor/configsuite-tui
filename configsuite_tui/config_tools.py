import yaml
from configsuite import ConfigSuite


def load(filename):
    with open(filename) as file:
        return yaml.full_load(file)


def save(config, filename):
    with open(filename, "w") as file:
        yaml.dump(config, file, sort_keys=False)


def validate(config, schema):
    return ConfigSuite(config, schema, deduce_required=True).valid
