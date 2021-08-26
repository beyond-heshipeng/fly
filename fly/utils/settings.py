from fly.settings import Settings
from fly.settings import default_settings


def get_settings(settings: dict = None):
    items = {}
    variables = dir(default_settings)
    for var in variables:
        if not var.startswith("_") and not var.islower():
            items[var] = eval(f"default_settings.{var}")

    if settings:
        return Settings(items | settings)

    return Settings(items)
