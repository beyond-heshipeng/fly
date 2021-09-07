from collections.abc import Mapping
from typing import Any


class CaseLessDict(dict):

    __slots__ = ()

    def __init__(self, seq=None):
        super().__init__()
        if seq:
            self.update(seq)

    def __getitem__(self, key):
        return dict.__getitem__(self, self.norm_key(key))

    def __setitem__(self, key, value):
        dict.__setitem__(self, self.norm_key(key), self.norm_value(value))

    def __delitem__(self, key):
        dict.__delitem__(self, self.norm_key(key))

    def __contains__(self, key):
        return dict.__contains__(self, self.norm_key(key))
    has_key = __contains__

    def __copy__(self):
        return self.__class__(self)
    copy = __copy__

    @classmethod
    def norm_key(cls, key):
        """Method to normalize dictionary key access"""
        return key.lower()

    @classmethod
    def norm_value(cls, value):
        """Method to normalize values prior to be setted"""
        return value

    def get(self, key, def_val=None):
        return dict.get(self, self.norm_key(key), self.norm_value(def_val))

    def setdefault(self, key, def_val=None):
        return dict.setdefault(self, self.norm_key(key), self.norm_value(def_val))

    def update(self, seq: Any) -> None:
        seq = seq.items() if isinstance(seq, Mapping) else seq
        is_eq = ((self.norm_key(k), self.norm_value(v)) for k, v in seq)
        super().update(is_eq)

    @classmethod
    def fromkeys(cls, keys, value=None):
        return cls((k, value) for k in keys)

    def pop(self, key, *args):
        return dict.pop(self, self.norm_key(key), *args)