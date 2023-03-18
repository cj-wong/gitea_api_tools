import json

from . import config
from . import utils


def get_user_id() -> int:
    """Get the user ID.

    Returns:
        int: user ID

    Raises:
        RuntimeError: could not get encoding

    """
    response = utils.get_url(f"{config.HOST_API}/user")
    if response.status_code != 200:
        raise RuntimeError("Could not user information")
    elif not response.encoding:
        raise RuntimeError(config.NO_ENCODING.format("user"))

    user = json.loads(response.content.decode(response.encoding))
    user_id = user['id']
    return int(user_id)


def main() -> None:
    """Get the user ID and optionally store it into the configuration."""
    user_id = get_user_id()
    config.logger.info(f"Your user ID is {user_id}.")
    choice = input("Would you like to store this in the configuration? [yN] ")
    if choice.lower().startswith('y'):
        config.CONF['uid'] = user_id
        config.write_config()
        config.logger.info("User ID was stored in config.json.")
    else:
        config.logger.info("User ID was not stored.")


if __name__ == '__main__':
    main()
