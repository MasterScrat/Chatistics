import yaml
import os
import logging


def get_config():
    log = logging.getLogger(__name__)
    # basic config
    with open('config.yml', 'r', encoding="utf8") as config_file:
        config = yaml.safe_load(config_file)
    # secrets
    for env_var in ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE']:
        config[env_var] = os.environ.get(env_var, '')
    return config


config = get_config()
