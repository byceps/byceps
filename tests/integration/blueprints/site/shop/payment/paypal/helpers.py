import json
from types import SimpleNamespace


def json_to_obj(json_text):
    return json.loads(json_text, object_hook=lambda d: SimpleNamespace(**d))
