# -*- coding: utf-8 -*-
# Simple JSON Encoder: Manually encode Python objects as JSON

def escape_string(s):
    """Escape string for JSON."""
    let result = ""
    for char in s:
        if char == '"':
            result = result + '\\"'
        elif char == '\\':
            result = result + '\\\\'
        elif char == '\n':
            result = result + '\\n'
        elif char == '\r':
            result = result + '\\r'
        elif char == '\t':
            result = result + '\\t'
        else:
            result = result + char
    return result

def encode_json(obj):
    """Encode Python object as JSON string."""
    if obj is None:
        return "null"
    elif obj is True:
        return "true"
    elif obj is False:
        return "false"
    elif isinstance(obj, str):
        return '"' + escape_string(obj) + '"'
    elif isinstance(obj, int):
        return str(obj)
    elif isinstance(obj, float):
        return str(obj)
    elif isinstance(obj, list):
        let list_items = [encode_json(item) for item in obj]
        return "[" + ", ".join(list_items) + "]"
    elif isinstance(obj, dict):
        let dict_items = []
        for key in obj:
            let encoded_key = encode_json(key)
            let encoded_val = encode_json(obj[key])
            dict_items.append(encoded_key + ": " + encoded_val)
        return "{" + ", ".join(dict_items) + "}"
    else:
        return "null"

# Test cases
print(encode_json({"a": 1, "b": [2, 3]}))
print(encode_json({"x": "hello"}))
print(encode_json(None))
print(encode_json(True))
print(encode_json(False))
