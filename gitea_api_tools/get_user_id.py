import json

from . import config
from . import gitea


config.validate()


def get_user_id() -> int:
    """Get the user ID.

    Returns:
        int: user ID

    Raises:
        RuntimeError: could not get encoding

    """
    url = f"{config.user_config.host_api}/user"
    try:
        response = gitea.api.get_response(url)
    except FileNotFoundError:
        raise RuntimeError("Could not user information")
    except ValueError:
        raise RuntimeError(gitea.api.ERR_NO_ENCODING.format("user"))

    user = json.loads(response)
    try:
        user_id = user["id"]
    except KeyError:
        raise RuntimeError("Could not get ID from response")

    return int(user_id)


def main() -> None:
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

    new_uid = get_user_id()
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


if __name__ == "__main__":
    main()
