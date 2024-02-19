import re
import sys
import time
from textwrap import dedent

from . import (
    Config,
    logger,
    user_config,
    user_config_path,
    _example,
    validate,
)

ERR_COULD_NOT_CONFIGURE = 1

CONFIRM = re.compile(r"^y", re.IGNORECASE)

JSON_TYPE = str | float | bool


def select_config() -> Config:
    """Select a configuration."""
    if user_config.fields:
        logger.warning("A configuration already exists.")
        ask_create_new = input("Overwrite this configuration? [yN] ")
        if not CONFIRM.match(ask_create_new):
            logger.info("Using existing configuration")
            return user_config
        else:
            wait = 5
            logger.info(f"Discarding previous configuration in {wait} seconds")
            time.sleep(wait)
            user_config.file.unlink()

    return Config(user_config_path)


def validate_input(field: str, value: JSON_TYPE, optional: bool) -> JSON_TYPE:
    """Validate input to match value type in example configuration.

    Args:
        field: field or key from configuration
        value: value from field
        optional: whether the value is optional or not in the example config

    Returns:
        JSON_TYPE: validated value with same type as example value

    """
    bools = {
        "True": True,
        "False": False,
    }

    message = f"Enter a value for {field}{' (optional)' if optional else ''}: "
    val_type = type(value)
    logger.info(f"The example value for {field} is {value}")
    if optional:
        logger.info("To skip this option, just hit Enter again")
    new_value = input(message)

    while True:
        if optional and not new_value:
            logger.info("Using default value from example")
            return value
        elif not optional and type(new_value) is val_type and new_value:
            return new_value

        if new_value.isdigit() and val_type is int:
            return int(new_value)

        capitalized = new_value.capitalize()
        if capitalized in bools:
            return bools[capitalized]

        try:
            floating = float(new_value)
            if val_type is float:
                return floating
        except (SyntaxError, TypeError, ValueError):
            pass

        logger.warning(f"Value must be {val_type}")
        new_value = input(message)

    return new_value


def overwrite_existing(field: str, existing_value: JSON_TYPE) -> bool:
    """Ask the user whether to overwrite the existing value or not.

    Args:
        field: field or key from configuration
        existing_value: the existing value

    Returns:
        bool: True if the user accepts overwriting old value; False otherwise

    """
    logger.warning(
        dedent(
            f"""\
            The existing configuration already has a value in "{field}".
            Old value: {existing_value}"""
        )
    )
    overwrite = input("Do you want to overwrite this? [yN] ")
    return bool(CONFIRM.match(overwrite))


def configure_interactively() -> None:
    """Configure the program interactively."""
    try:
        # As long as the example file exists, validation doesn't matter
        validate()
    except RuntimeError as e:
        logger.error(e)
        sys.exit

    sel_config = select_config()

    for field in _example.fields:
        value = getattr(_example, field)
        optional = not value
        if existing_value := getattr(sel_config, field, False):
            if not overwrite_existing(field, existing_value):
                continue
            else:
                logger.info(f"{field} will be overwritten")
        new_val = validate_input(field, value, optional)
        setattr(sel_config, field, new_val)

    if not validate(sel_config):
        logger.error("Could not configure correctly")
        sys.exit(ERR_COULD_NOT_CONFIGURE)

    sel_config.write_config()
