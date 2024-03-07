from . import formats
from . import python
from . import version


__all__ = [
    "formats",
    "python",
    "version",
]


class NotFound(BaseException):
    """No package matched."""

    def __init__(self) -> None:
        """Initialize with error message."""
        super().__init__("Package was not found")


class CouldNotParse(ValueError):
    """Dependency did not match expected format."""

    def __init__(self) -> None:
        """Initialize with error message."""
        super().__init__("Could not parse package name")
