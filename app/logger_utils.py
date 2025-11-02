from __future__ import annotations

# Very small deny-list based masking
DENY_KEYS = {"password", "token", "secret", "body"}


def _mask(value):
    if isinstance(value, str):
        return "***"
    if isinstance(value, (int, float)):
        return 0
    return "***"


def mask_pii(obj):
    """Return a shallow copy of obj with PII-like fields masked.
    Works for dict or list of dicts. Intended for logging.
    """
    if isinstance(obj, list):
        return [mask_pii(x) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k.lower() in DENY_KEYS:
                out[k] = _mask(v)
            else:
                out[k] = v
        return out
    return obj
