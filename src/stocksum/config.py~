import yaml
import os
import os.path

config = {
    'debug': False,
    'database': {
        'url':  'sqlite:///stocksum.db'
    },
    'logging': {
        'level': 'warning',
        'path': None,
        'max_size': 100 * 1000 * 1000,# ~ 95 mb
        'num_backups': 10,
    },
    'email': {
        'enabled': False,
        'server': '',
        'port': 587,
        'username': '',
        'password': '',
        'from_domain': '',
        'use_tls': False
    },
    'web': {
        'cookie_secret': '',
        'port': 8001,
        'google_oauth': {
            'client_id': '',
            'client_secret': '',
        },
        'base_url': 'http://localhost:8001',
    },
    'report': {
        'max_workers': 10,
        'path': '/var/stocksum/reports'
    }
}

def load(path=None):
    default_paths = [
        './stocksum.yaml',
        '~/stocksum.yaml',
    ]
    if not path:
        path = os.environ.get('stocksum_CONFIG', None)
        if not path:
            for p in default_paths:
                p = os.path.expanduser(p)
                if os.path.isfile(p):
                    path = p
                    break
    if not path:
        raise Exception('No config file specified.')
    if not os.path.isfile(path):
        raise Exception('Config: "{}" could not be found.'.format(path))
    with open(path) as f:
        data = yaml.load(f)
    for key in data:
        if key in config:
            if isinstance(config[key], dict):
                config[key].update(data[key])
            else:
                config[key] = data[key]
load()