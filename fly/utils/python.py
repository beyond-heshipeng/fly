import inspect
import os


def to_unicode(text, encoding=None, errors='strict'):
    """Return the unicode representation of a bytes object ``text``. If
    ``text`` is already an unicode object, return it as-is."""
    if isinstance(text, str):
        return text
    if not isinstance(text, (bytes, str)):
        raise TypeError('to_unicode must receive a bytes or str '
                        f'object, got {type(text).__name__}')
    if encoding is None:
        encoding = 'utf-8'
    return text.decode(encoding, errors)


def to_bytes(text, encoding=None, errors='strict'):
    """Return the binary representation of ``text``. If ``text``
    is already a bytes object, return it as-is."""
    if isinstance(text, bytes):
        return text
    if not isinstance(text, str):
        raise TypeError('to_bytes must receive a str or bytes '
                        f'object, got {type(text).__name__}')
    if encoding is None:
        encoding = 'utf-8'
    return text.encode(encoding, errors)


def without_none_values(iterable):
    """Return a copy of ``iterable`` with all ``None`` entries removed.

    If ``iterable`` is a mapping, return a dictionary where all pairs that have
    value ``None`` have been removed.
    """
    try:
        return {k: v for k, v in iterable.items() if v is not None}
    except AttributeError:
        return type(iterable)((v for v in iterable if v is not None))


class Defer:
    """
    Proof of concept for a python equivalent of golang's defer statement
    Note that the callback order is probably not guaranteed

    https://stackoverflow.com/questions/34625089/python-equivalent-of-golangs-defer-statement
    """
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

        # Add a reference to self in the caller variables so our __del__
        # method will be called when the function goes out of scope
        caller = inspect.currentframe().f_back
        caller.f_locals[b'_' + os.urandom(48)] = self

    def __del__(self):
        self.callback(*self.args, **self.kwargs)


# def defer(func):
#     @wraps(func)
#     def func_wrapper(*args, **kwargs):
#         with ExitStack() as stack:
#             stack.callback(partial(func, args, kwargs))
#
#     return func_wrapper
