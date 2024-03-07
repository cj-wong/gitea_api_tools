import os
import sys
from pathlib import Path


_PATHS = tuple[Path, Path]


def get_os_linux_dirs(project_name: str) -> _PATHS:
    """Get the directories for Linux (and Cygwin).

    Args:
        project_name: name of project

    Returns:
        _PATHS:

            1.  configuration directory; on Linux, it'd be XDG_CONFIG_HOME
            2.  cache/data directory; on Linux, it can be XDG_STATE_HOME

    """
    config_root = Path(
        os.environ.get("XDG_CONFIG_HOME", "~/.config")
    ).expanduser()
    config_dir = config_root / project_name
    config_dir.mkdir(parents=True, exist_ok=True)
    cache_root = Path(
        os.environ.get("XDG_STATE_HOME", "~/.local/state")
    ).expanduser()
    cache_dir = cache_root / project_name
    cache_dir.mkdir(parents=True, exist_ok=True)
    return (config_dir, cache_dir)


def get_os_windows_dirs(project_name: str) -> _PATHS:
    """Get the directories for Windows.

    Args:
        project_name: name of project

    Returns:
        _PATHS: for Windows, this is typically LOCALAPPDATA for both paths

    Raises:
        RuntimeError: LOCALAPPDATA could not be found

    """
    win32_err = (
        "Your OS reported itself as Windows but"
        " it's missing environment variables"
    )
    try:
        data_root = Path(os.environ.get("LOCALAPPDATA", "an_invalid_path"))
    except TypeError as e:
        raise RuntimeError(win32_err) from e
    data_dir = data_root / project_name
    data_dir.mkdir(parents=True, exist_ok=True)
    return (data_dir, data_dir)


def get_os_dirs(project_name: str) -> _PATHS:
    """Get directories corresponding to OS configuration/cache.

    Returns:
        _PATHS:

            1.  configuration directory
            2.  cache/data directory

    Raises:
        RuntimeError: for one of two reasons:

            1.  OS is not supported. Currently, only Linux (and by extension,
                cygwin) and Windows are supported.
            2.  Windows was detected but it's missing a critical environment
                variable: LocalAppData.

    """
    if sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        return get_os_linux_dirs(project_name)
    elif sys.platform.startswith("win32"):
        return get_os_windows_dirs(project_name)

    raise RuntimeError("This project does not support your operating system")
