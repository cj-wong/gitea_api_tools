import json
import logging
import logging.handlers
import re
import sys


# Logger related

_LOGGER_NAME = 'gitea_scanner'

LOGGER = logging.getLogger(_LOGGER_NAME)
LOGGER.setLevel(logging.DEBUG)

_FH = logging.handlers.RotatingFileHandler(
    f'{_LOGGER_NAME}.log',
    maxBytes=40960,
    backupCount=5,
    )
_FH.setLevel(logging.DEBUG)

_CH = logging.StreamHandler()
_CH.setLevel(logging.INFO)

_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
_FH.setFormatter(_FORMATTER)
_CH.setFormatter(_FORMATTER)

LOGGER.addHandler(_FH)
LOGGER.addHandler(_CH)

# Configuration file reading and validating

_CONFIG_LOAD_ERRORS = (
    FileNotFoundError,
    KeyError,
    TypeError,
    ValueError,
    json.decoder.JSONDecodeError,
    )

EXIT_CONFIG_INVALID = 1
EXIT_CONFIG_DEFAULT = 2
EXIT_CONFIG_DEFAULT_VALUES = 3
EXIT_CONFIG_EMPTY_VALUE = 4
EXIT_NO_ARGS = 10

try:
    with open('config.json') as f:
        CONF = json.load(f)
except _CONFIG_LOAD_ERRORS as e:
    LOGGER.error("config.json doesn't exist or is malformed.")
    LOGGER.error(f'More information: {e}')
    sys.exit(EXIT_CONFIG_INVALID)

with open('config.json.example') as f:
    _DEFAULTS = json.load(f)

TOKEN = CONF['token']
HOST = CONF['host']

if _DEFAULTS == CONF:
    LOGGER.error(
        "config.json has default values. Modify them with your own.")
    sys.exit(EXIT_CONFIG_DEFAULT)
elif not TOKEN or not HOST:
    LOGGER.error('"token" and "host" are required fields for config.json.')
    sys.exit(EXIT_CONFIG_EMPTY_VALUE)
elif TOKEN == _DEFAULTS['token']:
    LOGGER.error('Enter your own token under "token".')
    LOGGER.error("Reference: https://docs.gitea.io/en-us/api-usage/")
    sys.exit(EXIT_CONFIG_DEFAULT_VALUES)
elif HOST == _DEFAULTS['host']:
    LOGGER.error('Enter your own Gitea instance under "host".')
    sys.exit(EXIT_CONFIG_DEFAULT_VALUES)
elif 'uid' in CONF and type(CONF['uid']) is not int and not CONF['uid'].isnum():
    LOGGER.error('User IDs ("uid") are strictly numbers and optional.')
    LOGGER.error('If not used, delete the key-value pair for "uid".')
    sys.exit(EXIT_CONFIG_DEFAULT_VALUES)
elif 'uid' not in CONF:
    CONF['uid'] = 0

UID = int(CONF['uid'])
HOST_API = f"{HOST}/api/v1"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/json",
    }
SEARCH_ARCHIVED_REPOS = bool(CONF['search_archived_repos'])

# Other configuration

SWAGGER_API_LIMIT = 999_999_999
PACKAGE_VERSION = re.compile(r'^[0-9]\.[0-9]\.[0-9]$')
