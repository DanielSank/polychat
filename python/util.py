import os

import yaml


this_dir = os.path.dirname(os.path.abspath(__file__))
config_filepath = os.path.join(this_dir, '..', 'config.yaml')


def get_config(path=config_filepath):
    with open(path, 'r') as stream:
        result = yaml.load(stream)
    return result
