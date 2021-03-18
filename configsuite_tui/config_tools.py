import yaml
from configsuite import ConfigSuite


def load(filename):
    with open(filename, "r") as file:
        first_line = file.readline()

    with open(filename) as file:
        schema = None
        if "!# configsuite-tui" in first_line:
            next(file)
            schema = first_line.split("!# configsuite-tui: schema=")[1].strip()
        return yaml.full_load(file), schema


def save(config, filename, schema):
    with open(filename, "w") as file:
        file.write("!# configsuite-tui: schema=" + schema + "\n")
        yaml.dump(config, file, sort_keys=False)


def validate(config, schema):
    return ConfigSuite(config, schema, deduce_required=True).valid


def readable(config, schema):
    return ConfigSuite(config, schema, deduce_required=True).readable
