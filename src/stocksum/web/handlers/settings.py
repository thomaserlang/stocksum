import logging
import pytz
from stocksum.web.handlers import base
from tornado import auth, gen, httpclient, web
from stocksum.config import config
from stocksum.web import models, utils
from stocksum.web.decorators import new_session
from datetime import datetime

class Handler(base.Handler):

    @web.authenticated
    def get(self):
        with new_session() as session:
            user = session.query(models.User).get(self.current_user['id'])
            self.render(
                'settings.html',
                user=user,
                timezones=pytz.common_timezones,
            )

    @web.authenticated
    def post(self):
        with new_session() as session:
            name = self.get_argument('name')
            timezone = self.get_argument('timezone')
            if timezone not in pytz.common_timezones:
                self.set_status(400)
                self.write({
                    'error': 'unknown time zone',
                })
            if not name:
                name = None

            user = session.query(models.User).get(self.current_user['id'])
            user.name = name
            user.timezone = timezone
            session.commit()
            self.set_secure_cookie(
                'user',
                utils.json_dumps({
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'timezone': user.timezone,
                }),
                120
            )
            self.write({
                'status': 'OK',
            })