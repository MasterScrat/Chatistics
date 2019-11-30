import yaml
import os
import logging

def merge(current, override):
    if isinstance(current, dict) and isinstance(override, dict):
        for k, v in override.items():
            if k not in current or not isinstance(v, dict):
                current[k] = v
            else:
                current[k] = merge(current[k], v)
    return current

def get_config():
    log = logging.getLogger(__name__)
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    if os.path.isfile('secrets.yml'):
        with open('secrets.yml', 'r') as config_file:
            secrets = yaml.safe_load(config_file)
        config = merge(config, secrets)
    else:
        log.warning('Could not find secrets.yml')
    return config

config = get_config()
