import yaml


def get_config(path='config.yaml'):
    with open(path, 'r') as stream:
        result = yaml.load(stream)
    return result
