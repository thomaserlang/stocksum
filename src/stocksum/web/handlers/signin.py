import logging
from stocksum.web.handlers import base
from tornado import auth, gen, httpclient
from stocksum.config import config
from stocksum.web import models, utils, decorators
from stocksum.web.decorators import new_session
from datetime import datetime

class Handler(base.Handler):

    def get(self):
        self.render('signin.html')

class Google_handler(base.Handler, auth.GoogleOAuth2Mixin):

    @gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            response = yield self.get_authenticated_user(
                redirect_uri='{}/signin/google'.format(config['web']['base_url']),
                code=self.get_argument('code'),
            )
            user = yield httpclient.AsyncHTTPClient().fetch(
                'https://www.googleapis.com/oauth2/v1/userinfo?alt=json',
                method='GET',
                headers={
                    'Authorization': 'Bearer {}'.format(response['access_token']),
                }
            )
            user_data = utils.json_loads(user.body)
            logging.info(user_data)
            with new_session() as session:
                new_user = False
                user = session.query(models.User).filter(
                    models.User.email == user_data['email']
                ).first()
                new_user = False
                if not user:
                    new_user = True
                    user = models.User(
                        email=user_data['email'],
                        created=datetime.utcnow(),
                        name=user_data['name']
                    )
                    session.add(user)
                    session.flush()
                    user.name = str(user.id)
                    new_user = True
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
                session.commit()
            if new_user:
                self.redirect('/settings')
            else:
                self.redirect('/')
        else:
            yield self.authorize_redirect(
                redirect_uri='{}/signin/google'.format(config['web']['base_url']),
                client_id=config['web']['google_oauth']['client_id'],
                scope=['openid', 'profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'},
            )