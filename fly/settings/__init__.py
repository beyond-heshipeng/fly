import copy
import json
from collections import Mapping


class Settings(Mapping):
    """
    fly settings module class

    """

    def __init__(self, items: dict = None):
        self.frozen = False
        self.attributes = {}
        if items:
            for key, value in items.items():
                self.attributes[key] = value

    def __getitem__(self, opt_name):
        if opt_name not in self.attributes:
            return None

        return self.attributes[opt_name]

    def __contains__(self, name):
        return name in self.attributes

    def get(self, name, default=None):
        """
        Get a setting value without affecting its original type.
        """

        return self.attributes[name] if name in self else default

    def getboolean(self, name, default=False):
        """
        Get a setting value as a boolean.
        """

        got = self.get(name, default)
        try:
            return bool(int(got))
        except ValueError:
            if got in ("True", "true"):
                return True
            if got in ("False", "false"):
                return False
            raise ValueError("Supported values for boolean settings "
                             "are 0/1, True/False, '0'/'1', "
                             "'True'/'False' and 'true'/'false'")

    def getint(self, name, default=0):
        """
        Get a setting value as an int.
        """

        return int(self.get(name, default))

    def getfloat(self, name, default=0.0):
        """
        Get a setting value as a float.
        """

        return float(self.get(name, default))

    def getlist(self, name, default=None):
        """
        Get a setting value as a list. If the setting original type is a list, a
        copy of it will be returned. If it's a string it will be split by ",".
        """

        value = self.get(name, default or [])
        if isinstance(value, str):
            value = value.split(',')
        return list(value)

    def get_dict(self, name, default=None):
        """
        Get a setting value as a dictionary.
        """

        value = self.get(name, default or {})
        if isinstance(value, str):
            value = json.loads(value)
        return dict(value)

    def __setitem__(self, name, value):
        self.set(name, value)

    def set(self, name, value):
        """
        Store a key/value attribute.
        """

        self._assert_mutability()
        self.attributes[name] = value

    def update(self, values):
        """
        Store key/value pairs.
        """

        self._assert_mutability()
        if isinstance(values, str):
            values = json.loads(values)

        for name, value in values.items():
            self.set(name, value)

    def delete(self, name):
        self._assert_mutability()
        del self.attributes[name]

    def __delitem__(self, name):
        self._assert_mutability()
        del self.attributes[name]

    def _assert_mutability(self):
        if self.frozen:
            raise TypeError("Trying to modify an immutable Settings object")

    def copy(self):
        """
        Make a deep copy of current settings.
        """

        return copy.deepcopy(self)

    def freeze(self):
        """
        Disable further changes to the current settings.
        """

        self.frozen = True

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def __str__(self):
        return f"{type(self)}: {{" \
               + ", ".join([f"{key}: '{value}'"
                            if type(value) is str
                            else f"{key}: {value}"
                            for key, value in self.attributes.items()]) \
               + "}"
