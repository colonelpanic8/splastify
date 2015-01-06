import os

import pylast
import yaml

from .filters import *


def network_from_filepath(filename, cache_filepath=None):
    with open(filename, "r") as yaml_file:
        network_arguments = yaml.load(yaml_file)
    assert 'api_key' in network_arguments
    assert 'api_secret' in network_arguments
    network = pylast.LastFMNetwork(**network_arguments)
    if cache_filepath is not None:
        if cache_filepath is True:
            cache_filepath = os.path.join(os.path.dirname(__file__), "pylast_cache")
        network.enable_caching(file_path=cache_filepath)
    return network
