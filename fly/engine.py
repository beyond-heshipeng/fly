from fly.downloader import DownloaderManager
from fly.scheduler import Scheduler


class Engine:
    def __init__(self, scheduler: Scheduler, downloader_manager: DownloaderManager):