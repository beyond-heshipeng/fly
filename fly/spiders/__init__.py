# from typing import Optional
#
# from fly import Logger
# from fly.utils.settings import get_settings
#
#
# class SpiderBase(object):
#     name: Optional[str] = None
#     start_urls: Optional[list] = []
#
#     allowed_domains: list = []
#     allowed_status: list = []
#
#     custom_settings: Optional[dict] = {}
#
#     def __init__(self, name: str = None) -> None:
#         if name is not None:
#             self.name = name
#         elif not getattr(self, 'name', None):
#             raise ValueError(f"{type(self).__name__} must have a name")
#         if not hasattr(self, 'start_urls'):
#             self.start_urls = []
#
#         if hasattr(self, "custom_settings"):
#             custom_settings = getattr(self, "custom_settings")
#         else:
#             custom_settings = self.custom_settings
#         self.settings = get_settings(custom_settings)
#
#         self.logger = Logger(self.settings, self.name)
#
