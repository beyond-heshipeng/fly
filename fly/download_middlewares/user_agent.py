class UserAgentMiddleware:
    """This middleware allows spiders to override the user_agent"""

    def __init__(self, user_agent='Fly'):
        self.user_agent = user_agent

    @classmethod
    def from_settings(cls, settings):
        return cls(settings.get('USER_AGENT') or 'Fly')

    def process_request(self, request, spider):
        if self.user_agent:
            request.headers.setdefault('User-Agent', self.user_agent)
