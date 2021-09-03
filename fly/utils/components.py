import numbers
from operator import itemgetter

from fly.utils.python import without_none_values


def build_component_list(components_dict: dict):
    """Compose a component list from a { class: order } dictionary."""

    def _validate_values(comp_dict):
        if (t := type(components_dict)) is not dict:
            raise ValueError(f"Components must be a dict, got {t} instead")

        """Fail if a value in the components dict is not a real number or None."""
        for name, value in comp_dict.items():
            if value is not None and not isinstance(value, numbers.Real):
                raise ValueError(f'Invalid value {value} for component {name}, '
                                 'please provide a real number or None instead')

    _validate_values(components_dict)
    components_dict = without_none_values(components_dict)
    return [k for k, v in sorted(components_dict.items(), key=itemgetter(1))]
