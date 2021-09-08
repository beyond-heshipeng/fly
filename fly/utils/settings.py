from fly.settings import Settings
from fly.utils.python import without_none_values, without_empty_values


def get_settings(settings: dict = None):
    from fly.settings import default_settings

    items = {}
    variables = dir(default_settings)
    for var in variables:
        if not var.startswith("_") and not var.islower():
            items[var] = eval(f"default_settings.{var}")

    if settings:
        return Settings(items | without_empty_values(without_none_values(settings)))

    return Settings(items)
