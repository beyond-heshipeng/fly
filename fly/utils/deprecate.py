import warnings

from fly.exceptions import FlyDeprecationWarning

DEPRECATION_RULES = [
    ('fly.telnet.', 'fly.extensions.telnet.'),
]


def update_classpath(path):
    """Update a deprecated path from an object with its new location"""
    for prefix, replacement in DEPRECATION_RULES:
        if isinstance(path, str) and path.startswith(prefix):
            new_path = path.replace(prefix, replacement, 1)
            warnings.warn(f"`{path}` class is deprecated, use `{new_path}` instead",
                          FlyDeprecationWarning)
            return new_path
    return path
