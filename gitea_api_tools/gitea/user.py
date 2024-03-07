import json

from . import api
from .. import config


def get_id() -> int:
    """Get the user ID.

    Returns:
        int: user ID

    Raises:
        RuntimeError: could not get encoding

    """
    try:
        response = api.get_response("user")
    except FileNotFoundError:
        raise RuntimeError("Could not user information")
    except ValueError:
        raise RuntimeError(api.ERR_NO_ENCODING.format("user"))

    user = json.loads(response)
    try:
        return int(user["id"])
    except KeyError:
        raise RuntimeError("Could not get ID from response")
    except (TypeError, ValueError) as e:
        raise RuntimeError("The ID isn't a number") from e


def store_retrieved_id() -> None:
    """Get the user ID and optionally store it into the configuration."""
    old_uid = getattr(config.user_config, "uid")
    if old_uid:
        config.logger.warning(
            f"Your user ID ({old_uid}) has already been configured."
        )
        choice = input("Would you still like to proceed? [yN] ")
        if not choice.lower().startswith("y"):
            config.logger.info("Stopped.")
            return

    new_uid = get_id()
    config.logger.info(f"Your user ID is {new_uid}.")
    if old_uid and new_uid != old_uid:
        config.logger.warning(
            "This new user ID differs from the one stored in configuration."
        )
        choice = input("Would you still like to proceed? [yN] ")
        if not choice.lower().startswith("y"):
            config.logger.info("Stopped.")
            return
    elif old_uid:
        config.logger.info("This user ID is identical; no action is needed.")
        return

    choice = input("Would you like to store this in the configuration? [yN] ")
    if choice.lower().startswith("y"):
        setattr(config.user_config, "uid", new_uid)
        config.user_config.write_config()
        config.logger.info("User ID was stored in config.json.")
    else:
        config.logger.info("User ID was not stored.")
