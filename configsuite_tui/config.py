import yaml


def load(filename):
    with open(filename) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        return config
