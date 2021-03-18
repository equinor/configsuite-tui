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


def validate(config, schema, index):
    s = ConfigSuite(config, schema, deduce_required=True)
    error_list = get_page_errors(s.errors, index)
    return s.valid, error_list


def get_page_errors(errors, index):
    error_list = {}
    for error in errors:
        if error.key_path[0:-1] == tuple(index):
            error_list[error.key_path[-1]] = error.msg
    return error_list


def readable(config, schema):
    return ConfigSuite(config, schema, deduce_required=True).readable
