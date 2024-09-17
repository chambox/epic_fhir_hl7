from flask import current_app as app
import os
import json
import time, math


def cache_file(key):
    return os.path.join("cache", "cache-%s.json" % (key,))


def cache_set(key, value, timeout=9600):
    jsonfile = cache_file(key)
    data = {"expires": math.ceil(time.time()) + timeout, "value": value}

    try:
        with open(jsonfile, "w") as file:
            file.write(json.dumps(data, indent=4))

        return True
    except:
        return False


def cache_get(key):
    jsonfile = cache_file(key)
    try:
        if os.path.exists(jsonfile):
            with open(jsonfile) as file:
                data = json.load(file)

            if data["expires"] < time.time():
                return None

            return data["value"]
    except:
        cache_delete(key)
        return None


def cache_delete(key):
    jsonfile = cache_file(key)
    if os.path.exists(jsonfile):
        os.remove(jsonfile)


def get_json_data(jsonfile):
    file = os.path.join(app.root_path, "data", jsonfile)
    if os.path.exists(file):
        with open(file) as sf:
            return json.load(sf)
