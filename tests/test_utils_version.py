import unittest

from gitea_api_tools.package.version import Version


class TestVersion(unittest.TestCase):
    """Tests the version class in utils."""

    # The tuples in this list correspond to the tests attempted in
    # test_version_greater() and test_version_less() in sequential order.
    # Each pair must have the same number of components.
    comparison_versions = [
        ("2.0.0", "1.0.0"),
        ("2.0.0", "1.1.0"),
        ("1.10.0", "1.9.9"),
    ]

    def test_version_equals(self) -> None:
        """Test that versions are equal.

        Versions are only equal if their components are the same length and
        the components are all the same value.

        """
        self.assertEqual(Version("1.0.0"), Version("1.0.0"))
        self.assertEqual(Version("1.0"), Version("1.0"))
        self.assertEqual(Version("1000"), Version("1000"))
        self.assertEqual(Version("1.0.0a"), Version("1.0.0a"))

    def test_version_not_equals(self) -> None:
        """Check that versions shouldn't be equal."""
        self.assertNotEqual(Version("1.0.0"), Version("1.0"))
        self.assertNotEqual(Version("1.0.0"), Version("1.0.1"))
        self.assertNotEqual(Version("1.0.0"), Version("1.0.0a"))

    def test_version_greater(self) -> None:
        """Test that one version is greater than the other.

        Check that x_l.y_l.z_l > x_r.y_r.z_r where...

        1. x_l > x_r
        2. x_l > x_r but y_l < y_r
        3. x_l == x_r and y_l > y_r but string sort would otherwise assume
           y_r > y_l

        Note that versions don't need to be in x.y.z format.

        """
        for left, right in self.comparison_versions:
            self.assertGreater(Version(left), Version(right))

    def test_version_less(self) -> None:
        """Test that one version is less than the other.

        Check that x_l.y_l.z_l < x_r.y_r.z_r where...

        1. x_l < x_r
        2. x_l < x_r but y_l > y_r
        3. x_l == x_r and y_l < y_r but string sort would otherwise assume
           y_r > y_l

        Note that versions don't need to be in x.y.z format.

        """
        # Unlike test_version_greater, right and left are swapped.
        for right, left in self.comparison_versions:
            self.assertLess(Version(left), Version(right))
