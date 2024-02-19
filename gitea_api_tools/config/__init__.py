import json
import sys
from pathlib import Path
from typing import Dict

from . import logging
from . import paths


_PROJECT_NAME = 'gitea-api-tools'
_CONFIG = Dict[str, str | int]


# Configuration file reading and validating


class Config:
    """Represents the configuration file as an object.

    Note that the object makes no attempt to validate the attributes when
    initializing.

    However, this class is designed specifically to compare the user config
    with the example. To do so, use the method is_config_ok().

    """

    _exit_invalid = 1
    _load_errors = (
        TypeError,
        ValueError,
        json.decoder.JSONDecodeError,
        )
    # _ok_same_value is a list of keys in which values can be the same
    # between the user and sample configurations.
    _ok_same_value = [
        "uid",
        "search_archived_repos",
        ]

    def __init__(self, file: Path) -> None:
        """Initialize the configuration class with the file."""
        self.file = file

        try:
            with file.open() as _f:
                contents = json.load(_f)
        except FileNotFoundError:
            logger.error(f"{file} does not exist")
            sys.exit(self._exit_invalid)
        except self._load_errors as e:
            logger.error(
                f"{file} exists but is malformed. More info:\n{e}")
            sys.exit(self._exit_invalid)

        for attr, val in contents.items():
            setattr(self, attr, val)
            if attr == 'host':
                self.host_api = f"{val}/api/v1"

        self.keys = contents.keys()

    def get_as_dict(self) -> _CONFIG:
        """Convert the configuration back into a dictionary.

        Returns:
            _CONFIG: a dictionary equivalent to config.json

        """
        as_dict: _CONFIG = {}
        for key in _example.keys:
            as_dict[key] = getattr(self, key)

        return as_dict

    def write_config(self) -> None:
        """Write (valid) configuration back to file.

        Raises:
            RuntimeError: could not validate configuration

        """
        if not validate(self):
            raise RuntimeError("Could not validate configuration")

        as_dict = self.get_as_dict()

        with self.file.open('w') as f:
            json.dump(as_dict, fp=f, indent=4)

        with self.file.open('a') as f:
            f.write('\n')


config_dir, cache_dir = paths.get_os_dirs(_PROJECT_NAME)
logger = logging.create_logger(_PROJECT_NAME, cache_dir)

user_config = Config(config_dir / 'config.json')
_example = Config(Path(__file__).parent / 'config.json.example')


def validate(u_config: Config = user_config) -> bool:
    """Validate the configuration.

    Args:
        u_config: user config; defaults to already instantiated user_config

    Returns:
        bool: True if the user (or supplied) config is valid; False otherwise

    """
    for key in _example.keys:
        try:
            user_val = getattr(user_config, key)
        except KeyError:
            return False

        try:
            ex_val = getattr(_example, key)
        except AttributeError:
            return False
        except NameError:
            raise RuntimeError("The example configuration was not found")

        if user_val == ex_val and key not in user_config._ok_same_value:
            return False

    return True


# Post-validation variables

# Other configuration

__all__ = [
    "logging",
    "paths",
]
