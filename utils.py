import re
from base64 import b64decode

import requests

import config


def request_get(url: str) -> requests.models.Response:
    """Call requests.get with headers from config."""
    return requests.get(url, headers=config.HEADERS)


def decode(text: str, encoding: str) -> str:
    """Decode provided text with its encoding.

    This function is to be used with API calls that may not return encoding in
    UTF-8. For example, some API calls return Base64 encoding.

    It's uncertain whether Gitea has other encoding besides Base64, however.

    Args:
        text: encoded text
        encoding: encoding of text

    Returns:
        str: decoded text

    Raises:
        ValueError: unknown encoding provided

    """
    known_encodings = {
        'base64': lambda text: b64decode(text).decode(),
        }

    if encoding not in known_encodings:
        raise ValueError(f"Unknown encoding {encoding}")

    return known_encodings[encoding](text).strip()


class Version:
    """Defines a version.

    Versions can be in a few formats:

    - x.y.z
    - x.y
    - x

    Version format x.y.z is perhaps the most common (usually using semver).
    Sometimes, a letter may be appended at the end (e.g. 1.0.0a) to indicate a
    beta release. Even so, '0a' would be greater than '0', for example.

    Nonetheless, versions are almost always delimited by dots and almost always
    only contain integers.

    """

    suffix = re.compile(r"^([0-9]+)([a-z])$", re.IGNORECASE)

    def __init__(self, ver_str: str) -> None:
        """Initialize the version with its string form.

        Args:
            ver_str (str): version in string form

        """
        self.original = ver_str
        parts = ver_str.split('.')
        last = self.suffix.match(parts[-1])
        if last:
            self.parts = [int(x) for x in parts[:-1]]
            self.parts.append(int(last.group(1)))
            # Convert the letter to an integer representing its position in the
            # alphabet with 0 index.
            self.parts.append(ord(last.group(2).lower()) - ord('a'))
        else:
            self.parts = [int(x) for x in parts]

    def __str__(self) -> str:
        """Return the original string representation."""
        return self.original

    def __eq__(self, other: object) -> bool:
        """Check two versions for equality."""
        if not isinstance(other, Version):
            return False

        if len(self.parts) != len(other.parts):
            return False

        for this, that in zip(self.parts, other.parts):
            if this != that:
                return False

        return True

    def __gt__(self, other: object) -> bool:
        """Check if this version is greater than the other."""
        if not isinstance(other, Version):
            raise TypeError

        if len(self.parts) != len(other.parts):
            raise ValueError("Number of components don't match")

        for this, that in zip(self.parts, other.parts):
            if this < that:
                return False
            elif this > that:
                return True

        return False

    def __lt__(self, other: object) -> bool:
        """Check if this version is less than the other."""
        if not isinstance(other, Version):
            raise TypeError

        if len(self.parts) != len(other.parts):
            raise ValueError("Number of components don't match")

        for this, that in zip(self.parts, other.parts):
            if this > that:
                return False
            elif this < that:
                return True

        return False


class NoDependency(BaseException):
    """No dependency matched."""

    def __init__(self) -> None:
        """Initialize with error message."""
        super().__init__("Dependency was not found")


class MismatchedDependency(ValueError):
    """Dependency had a different format and couldn't be directly compared."""

    def __init__(self) -> None:
        """Initialize with error message."""
        super().__init__("Dependency could not be compared")


class CouldNotParseDependency(ValueError):
    """Dependency did not match expected format."""

    def __init__(self) -> None:
        """Initialize with error message."""
        super().__init__("Could not parse dependency")
