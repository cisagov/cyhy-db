"""Test utils/decorators.py functionality."""

# Third-Party Libraries
import pytest

# cisagov Libraries
from cyhy_db.utils.decorators import deprecated


def test_deprecated_decorator_with_reason():
    """Test the deprecated decorator with a reason."""

    @deprecated("Use another function")
    def old_function():
        """Impersonate a deprecated function."""
        return "result"

    with pytest.warns(
        DeprecationWarning,
        match="old_function is deprecated and will be removed in a future version. Use another function",
    ):
        result = old_function()
        assert result == "result"


def test_deprecated_decorator_without_reason():
    """Test the deprecated decorator without a reason."""

    @deprecated(None)
    def old_function():
        """Impersonate a deprecated function."""
        return "result"

    with pytest.warns(
        DeprecationWarning,
        match="old_function is deprecated and will be removed in a future version.",
    ):
        result = old_function()
        assert result == "result"
