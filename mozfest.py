# from http://flask.pocoo.org/snippets/56/
from datetime import timedelta
from flask import make_response, request, current_app, jsonify
from functools import update_wrapper
from werkzeug.contrib.cache import SimpleCache


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


import requests
from flask import Flask

app = Flask(__name__)
cache = SimpleCache()


@app.route('/')
def ping():
    return 'pong'


@app.route('/schedule')
@crossdomain(origin='*')
def github_data():
    url = 'http://schedule.mozillafestival.org/schedule'
    json = cache.get(url)
    if json is None:
        json = requests.get(url).json()
        cache.set(url, json, timeout=5 * 60)
    return jsonify(json)
