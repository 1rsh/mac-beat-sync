import yaml
from copy import deepcopy

class DotDict(dict):
    def __getattr__(self, key):
        value = self.get(key)
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
            self[key] = value  # cache it
        return value

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]


_GLOBAL_OVERRIDES = {}


def _deep_merge(a: dict, b: dict) -> dict:
    """Return a new dict merging b into a (b takes precedence)."""
    result = deepcopy(a)
    for k, v in b.items():
        if (
            k in result
            and isinstance(result[k], dict)
            and isinstance(v, dict)
        ):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def set_config_overrides(overrides: dict) -> None:
    """Set runtime overrides (used by CLI). Overrides should be a nested dict mapping the same keys as config.yaml.

    Example: set_config_overrides({"audio": {"SAMPLE_RATE": 48000}})
    """
    global _GLOBAL_OVERRIDES
    if not isinstance(overrides, dict):
        raise TypeError("overrides must be a dict")
    _GLOBAL_OVERRIDES = deepcopy(overrides)


def get_config():
    """Load config.yaml and apply any runtime overrides previously set via set_config_overrides.

    Returns a DotDict with attribute-style access.
    """
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f) or {}

    if _GLOBAL_OVERRIDES:
        merged = _deep_merge(config, _GLOBAL_OVERRIDES)
    else:
        merged = config

    return DotDict(merged)