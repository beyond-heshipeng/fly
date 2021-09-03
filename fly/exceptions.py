class InvalidRequestMethodErr(Exception):
    pass


class InvalidDownloadMiddlewareErr(Exception):
    pass


class InvalidMiddlewareErr(Exception):
    pass


class QueueEmptyErr(Exception):
    pass


class FlyDeprecationWarning(Warning):
    """Warning category for deprecated features, since the default
    DeprecationWarning is silenced on Python 2.7+
    """
    pass
