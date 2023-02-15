import json

import config
import utils


def get_user_id() -> int:
    """Get the user ID.

    Returns:
        int: user ID

    Raises:
        RuntimeError: could not get encoding

    """
    response = utils.request_get(f"{config.HOST_API}/user")
    if not response.encoding:
        raise RuntimeError(config.NO_ENCODING.format("user"))

    user = json.loads(response.content.decode(response.encoding))
    user_id = user['id']
    return int(user_id)


def main() -> None:
    """Get the user ID and optionally store it into the configuration."""
    user_id = get_user_id()
    config.LOGGER.info(f"Your user ID is {user_id}.")
    choice = input("Would you like to store this in the configuration? [yN] ")
    if choice.lower().startswith('y'):
        config.CONF['uid'] = user_id
        config.write_config()
        config.LOGGER.info("User ID was stored in config.json.")
    else:
        config.LOGGER.info("User ID was not stored.")


if __name__ == '__main__':
    main()
