import logging
import pytz
from tornado import web
from stocksum.web import utils
from datetime import datetime

class Handler(web.RequestHandler):

    def get_template_namespace(self):
        namespace = web.RequestHandler.get_template_namespace(self)
        namespace.update(
            title='Stocksum.net',
            user_time=self.user_time,
        )
        return namespace

    def get_current_user(self):
        user = self.get_secure_cookie('user')
        if user:
            return utils.json_loads(user)

    def user_time(self, dt=None):
        if not dt:
            dt = datetime.utcnow()
        return datetime.astimezone(
            dt.replace(tzinfo=pytz.utc),
            pytz.timezone(self.current_user['timezone']),
        )

class API_handler(Handler):

    def set_default_headers(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, If-Match, If-Modified-Since, If-None-Match, If-Unmodified-Since, X-Requested-With')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE')
        self.set_header('Access-Control-Expose-Headers', 'ETag, Link, X-Total-Count, X-Total-Pages')
        self.set_header('Access-Control-Max-Age', '86400')
        self.set_header('Access-Control-Allow-Credentials', 'true')

    def write_object(self, obj):
        self.write(
            utils.json_dumps(obj, indent=4),
        )
