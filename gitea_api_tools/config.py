import json
import logging
import logging.handlers
import os
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
            logger.error(f"{file} exists but is malformed. More info:\n{e}")
            sys.exit(self._exit_invalid)

        for attr, val in contents.items():
            setattr(self, attr, val)
            if attr == 'host':
                self.host_api = f"{val}/api/v1"

        self.keys = contents.keys()

    def validate(self) -> bool:
        """Check whether the user supplied configuration is usable.

        Returns:
            bool: True if the user config is usable; False otherwise

                Specifically, if the user configuration contains any key-values
                that are unchanged from the example, then return False. If any
                keys are missing, then also return False.

        """
        for key in _example.keys:
            ex_val = getattr(self, key)

            try:
                user_val = getattr(_example, key)
            except AttributeError:
                return False
            except NameError:
                raise RuntimeError("The example configuration was not found")

            if ex_val == user_val and key not in self._ok_same_value:
                return False

        return True

    def write_config(self) -> None:
        """Write (valid) configuration back to file.

        Raises:
            RuntimeError: could not validate configuration

        """
        if not self.validate():
            raise RuntimeError("Could not validate configuration")

        with self.file.open('w') as f:
            json.dump(config, fp=f, indent=4)

        with self.file.open('a') as f:
            f.write('\n')


config_dir, cache_dir = get_os_dirs()
logger = create_logger(cache_dir)

config = Config(config_dir / 'config.json')
_example = Config(Path(__file__).parent / 'config.json.example')
if not config.validate():
    raise RuntimeError("Could not validate configuration")


# Post-validation variables

HEADERS = {
    "Authorization": f"token {getattr(config, 'token')}",
    "Accept": "application/json",
    }

# Other configuration

SWAGGER_API_LIMIT = 999_999_999
