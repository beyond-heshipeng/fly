import logging
import sys

from rich.logging import RichHandler
from fly.settings import Settings


class Logger:
    def __init__(self, settings: Settings = None, name: str = None):
        self.settings = settings or Settings()
        self.root = logging.getLogger(name)

        self._logging_format = self.settings.get("LOG_FORMAT", "%(asctime)s [%(name)s] %(levelname)s: %(message)s")

        self._logger_format()
        self._add_handler()

    @property
    def name(self):
        return self.root.name

    @name.setter
    def name(self, name):
        self.root.name = name

    def _logger_format(self):
        logging_level = self.settings.get("LOG_LEVEL", "DEBUG")

        logging.basicConfig(
            format=self._logging_format,
            level=logging_level,
            datefmt=self.settings.get("DATE_FORMAT", "%Y-%m-%d %H:%M:%S %Y"),
            handlers=[RichHandler(rich_tracebacks=True, show_time=False, show_path=False)]
        )

    def _add_handler(self):
        if self.settings.getboolean("LOG_STDOUT", False):
            self.root.addHandler(logging.StreamHandler(sys.stdout))

        if filename := self.settings.get("LOG_FILE"):
            file_handler = logging.FileHandler(filename, encoding=self.settings.get("LOG_ENCODING", "utf-8"))
            file_handler.setFormatter(logging.Formatter(self._logging_format))
            self.root.addHandler(file_handler)

    def info(self, msg, *args, **kwargs):
        if self.settings.getboolean("LOG_ENABLED", True):
            self.root.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.settings.getboolean("LOG_ENABLED", True):
            self.root.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.settings.getboolean("LOG_ENABLED", True):
            self.root.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.settings.getboolean("LOG_ENABLED", True):
            self.root.error(msg, *args, **kwargs)

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

