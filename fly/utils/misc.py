from importlib import import_module
from typing import Union, TypeVar

from fly.settings import Settings


SpiderType = TypeVar("SpiderType", bound="Spider")


def load_object(path):
    """Load an object given its absolute object path, and return it.

    eg: fly.http.request.Request, load Request object.
    """

    if not isinstance(path, str):
        if callable(path):
            return path
        else:
            raise TypeError("Unexpected argument type, expected string "
                            "or object, got: %s" % type(path))

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError(f"Error loading object '{path}': not a full path")

    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError(f"Module '{module}' doesn't define any object named '{name}'")

    return obj


def create_instance(obj_cls, obj: Union[Settings, SpiderType], *args, **kwargs):
    """Construct a class instance
    """
    if hasattr(obj_cls, 'from_spider'):
        instance = obj_cls.from_spider(obj, *args, **kwargs)
    elif hasattr(obj_cls, 'from_settings'):
        instance = obj_cls.from_settings(obj, *args, **kwargs)
    else:
        instance = obj_cls(*args, **kwargs)
    if instance is None:
        raise TypeError(f"{obj_cls.__qualname__} returned None")
    return instance
