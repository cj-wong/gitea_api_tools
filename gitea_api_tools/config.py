import json
import logging
import logging.handlers
import os
import re
import sys
from pathlib import Path
from typing import Tuple


_PROJECT_NAME = 'gitea-api-tools'


def get_os_dirs() -> Tuple[Path, Path]:
    """Get directories corresponding to OS configuration/cache.

    Returns:
        Tuple[Path, Path]:

            1.  configuration directory; on Linux, it'd be XDG_CONFIG_HOME
            2.  cache/data directory; on Linux, it can be XDG_STATE_HOME

    Raises:
        RuntimeError: for one of two reasons:

            1.  OS is not supported. Currently, only Linux (and by extension,
                cygwin) and Windows are supported.
            2.  Windows was detected but it's missing a critical environment
                variable: LocalAppData.

    """
    win32_err = (
        "Your OS reported itself as Windows but"
        " it's missing environment variables")
    if sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        config_root = Path(
            os.environ.get('XDG_CONFIG_HOME', '~/.config')).expanduser()
        config_dir = config_root / _PROJECT_NAME
        config_dir.mkdir(parents=True, exist_ok=True)
        cache_root = Path(
            os.environ.get('XDG_STATE_HOME', '~/.local/state')).expanduser()
        cache_dir = cache_root / _PROJECT_NAME
        cache_dir.mkdir(parents=True, exist_ok=True)
        return (config_dir, cache_dir)
    elif sys.platform.startswith("win32"):
        try:
            data_root = Path(os.environ.get('LOCALAPPDATA'))
        except TypeError as e:
            raise RuntimeError(win32_err) from e
        data_dir = data_root / _PROJECT_NAME
        data_dir.mkdir(parents=True, exist_ok=True)
        return (data_dir, data_dir)

    raise RuntimeError("This project does not support your operating system")


# Logger related


def create_logger(cache_dir: Path) -> logging.Logger:
    """Create logger into the cache directory.

    Args:
        cache_dir: the path to the cache directory for logging

    Returns:
        logging.Logger: the logger

    """
    log_file = cache_dir / f'{_PROJECT_NAME}.log'
    max_log_size = 40960
    max_log_files = 5

    logger = logging.getLogger(_PROJECT_NAME)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_log_size,
        backupCount=max_log_files,
        )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(
            '%(levelname)s - %(message)s'
            )
        )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


config_dir, cache_dir = get_os_dirs()
logger = create_logger(cache_dir)

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
EXIT_CONFIG_MISSING_REQUIRED = 5
EXIT_NO_ARGS = 10

try:
    with open('config.json') as _f:
        config = json.load(_f)
except _CONFIG_LOAD_ERRORS as e:
    logger.error("config.json doesn't exist or is malformed.")
    logger.error(f'More information: {e}')
    sys.exit(EXIT_CONFIG_INVALID)

with open('config.json.example') as _f:
    _DEFAULTS = json.load(_f)


def validate_configuration() -> None:
    """Validate the configuration."""
    exit = 0

    required_fields = {"host", "token", "search_archived_repos"}
    fields = set(config.keys())

    if _DEFAULTS == config:
        logger.error(
            "config.json has default values. Modify them with your own.")
        exit = EXIT_CONFIG_DEFAULT
    elif not required_fields.issubset(fields):
        logger.error("config.json is missing required fields.")
        exit = EXIT_CONFIG_MISSING_REQUIRED
    elif not config['token'] or not config['host']:
        logger.error('"token" and "host" are required fields for config.json.')
        exit = EXIT_CONFIG_EMPTY_VALUE
    elif config['token'] == _DEFAULTS['token']:
        logger.error('Enter your own token under "token".')
        logger.error("Reference: https://docs.gitea.io/en-us/api-usage/")
        exit = EXIT_CONFIG_DEFAULT_VALUES
    elif config['host'] == _DEFAULTS['host']:
        logger.error('Enter your own Gitea instance under "host".')
        exit = EXIT_CONFIG_DEFAULT_VALUES
    elif 'uid' in config:
        if type(config['uid']) is not int and not config['uid'].isnum():
            logger.error('User IDs ("uid") are strictly numbers and optional.')
            logger.error('If not used, delete the key-value pair for "uid".')
            exit = EXIT_CONFIG_DEFAULT_VALUES
    elif 'uid' not in config:
        config['uid'] = 0

    if exit:
        sys.exit(exit)


def write_config() -> None:
    """Write (valid) configuration back to file."""
    validate_configuration()

    with open('config.json', 'w') as f:
        json.dump(config, fp=f, indent=4)

    with open('config.json', 'a') as f:
        f.write('\n')


validate_configuration()

# Post-validation variables

UID = int(config['uid'])
HOST_API = f"{config['host']}/api/v1"
HEADERS = {
    "Authorization": f"token {config['token']}",
    "Accept": "application/json",
    }
SEARCH_ARCHIVED_REPOS = bool(config['search_archived_repos'])

# Other configuration

SWAGGER_API_LIMIT = 999_999_999
PACKAGE_VERSION = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')
NO_ENCODING = "No encoding was detected when {}"
