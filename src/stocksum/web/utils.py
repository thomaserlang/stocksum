import base64
import time
import os
import datetime
import re
import tornado.escape

try:
    import ujson as json
except ImportError:
    import json

def random_key():
    return base64.b64encode(
        os.urandom(30)
    ).decode('utf-8')

class JsonEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso
        if isinstance(value, set):
            return list(value)
        if hasattr(value, 'to_dict'):
            return value.to_dict()
        return super(JsonEncoder, self).default(value)

def _iso_datetime(value):
    """
    If value appears to be something datetime-like, return it in ISO format.

    Otherwise, return None.
    """
    if isinstance(value, datetime.datetime):
        return value.isoformat()+'Z'
    elif isinstance(value, datetime.time):
        return value.strftime('%H:%M:%S')
    elif isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')

def json_dumps(obj, **kwargs):
    '''
    Turns a object into a json string.

    :param obj: object
    :returns: str
    '''
    return json.dumps(
        obj,
        cls=JsonEncoder,
        **kwargs
    ).replace("</", "<\\/")

def json_loads(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return json.loads(s)

def dict_update(d1, d2):
    '''
    Updates values in `d1` with `d2`.
    Sub dicts will not be overwritten, but updated instead.

    :param d: dict
    :param update: dict
    '''
    for key in d2:
        if key in d1:
            if isinstance(d1[key], dict):
                d1[key].update(d2[key])
            else:
                d1[key] = d2[key]
        else:
            d1[key] = d2[key]
    return d1

def decode_dict(d, decoding='utf-8'):
    return {k.decode(decoding): v.decode(decoding) for k, v in d.items()}

def url_encode_tornado_arguments(arguments):
    '''
    Converts the following:

        {
            'param1': ['a', 'b'],
            'param2': ['c'],
        }

    into the following string:

        param1=a&param1=b&param2=c

    :arguemnts: dict
    :returns: str
    '''
    return '&'.join(
        ['{}={}'.format(arg, tornado.escape.url_escape(value.decode('utf-8') if isinstance(value, bytes) else str(value))) for arg in arguments for value in arguments[arg]]
    )

def parse_link_header(link_header):
    '''
    Parses a Link header into a dict according to: http://tools.ietf.org/html/rfc5988#page-6.

    Example:

        <https://api.example.com/1/users?page=2&per_page=1>; rel="next", <https://api.example.com/1/users?page=3&per_page=1>; rel="last"

    Turns into:

        {
            'next': 'https://api.example.com/1/users?page=2&per_page=1',
            'last': 'https://api.example.com/1/users?page=3&per_page=1'
        }

    :param link_header: str
    :returns: dict
    '''
    links = link_header.split(',')
    parsed_links = {}
    for link in links:
        segments = link.split(';')
        if len(segments) < 2:
            continue
        link_part = segments.pop(0).strip()
        if not link_part.startswith('<') or not link_part.endswith('>'):
            continue
        link_part = link_part[1:-1]
        for segment in segments:
            rel = segment.strip().split('=')
            if len(rel) < 2 or rel[0] != 'rel':
                continue
            rel_value = rel[1]
            if rel_value.startswith('"') and rel_value.endswith('"'):
                rel_value = rel_value[1:-1]
            parsed_links[rel_value] = link_part
    return parsed_links