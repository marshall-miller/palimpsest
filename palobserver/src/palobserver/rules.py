import re, yaml, pathlib

_CACHE = None

def _load_rules(path="rules/core.yaml"):
    global _CACHE
    if _CACHE is None:
        _CACHE = yaml.safe_load(pathlib.Path(path).read_text())
    return _CACHE

def flags(text: str, path="rules/core.yaml"):
    out = []
    for rule in _load_rules(path):
        if re.search(rule["pattern"], text, re.I):
            out.append(rule["code"])
    return out

