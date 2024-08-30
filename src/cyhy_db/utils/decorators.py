"""Decorators for the cyhy_db package."""

# Standard Python Libraries
import warnings


def deprecated(reason):
    """Mark a function as deprecated."""

    def decorator(func):
        if isinstance(reason, str):
            message = f"{func.__name__} is deprecated and will be removed in a future version. {reason}"
        else:
            message = f"{func.__name__} is deprecated and will be removed in a future version."

        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator
