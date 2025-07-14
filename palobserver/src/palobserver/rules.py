import re, yaml, pathlib, functools
from collections import defaultdict

# Global cache
_CACHE = None

def _load_rules(path: str):
    global _CACHE
    if _CACHE is None:
        raw = pathlib.Path(path).read_text()
        _CACHE = yaml.safe_load(raw)
    return _CACHE

@functools.lru_cache(maxsize=None)
def flags(text: str) -> list[str]:
    """
    Return shard-level flags (rule['code']) for rules without 'extract'.
    """
    rules = _load_rules("rules/core.yaml")
    out = []
    for rule in rules:
        if rule.get("extract"):
            continue
        if re.search(rule["pattern"], text, flags=re.IGNORECASE):
            out.append(rule["code"])
    return out

@functools.lru_cache(maxsize=None)
def extracts(text: str) -> dict[str, list[str]]:
    """
    Return a dict mapping extract names to lists of captured groups.
    E.g. {'net_days': ['30', '45']}
    """
    rules = _load_rules("rules/core.yaml")
    extras = defaultdict(list)
    for rule in rules:
        if not rule.get("extract"):
            continue
        m = re.search(rule["pattern"], text, flags=re.IGNORECASE)
        if m:
            extras[rule["extract"]].append(m.group(1))
    return dict(extras)

