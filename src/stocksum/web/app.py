import tornado.httpserver
import tornado.ioloop
import tornado.options
import logging
import os
import handlers.signin
import handlers.portfolios
import handlers.settings
import modules.portfolios_menu
import modules.portfolio_buttons
from tornado import web
from tornado.web import URLSpec
from stocksum.config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from stocksum.logger import Logger

class Application(web.Application):

    def __init__(self, **args):
        static_path = os.path.join(os.path.dirname(__file__), 'static')

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=static_path,
            debug=config['debug'],
            autoescape=None,
            xsrf_cookies=True,
            cookie_secret=config['web']['cookie_secret'],
            login_url='/signin',
            ui_modules=dict(
                portfolios_menu=modules.portfolios_menu.Module,
                portfolio_buttons=modules.portfolio_buttons.Module,
            ),
            google_oauth=dict(
                key=config['web']['google_oauth']['client_id'],
                secret=config['web']['google_oauth']['client_secret'],
            )
        )
        urls = [
            URLSpec(r'/favicon.ico', web.StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
            URLSpec(r'/static/(.*)', web.StaticFileHandler, {'path': static_path}),
            URLSpec(r'/signin/google', handlers.signin.Google_handler),
            URLSpec(r'/signin', handlers.signin.Handler),
            URLSpec(r'/settings', handlers.settings.Handler),
            URLSpec(r'/', handlers.portfolios.Handler),

            URLSpec(r'/portfolios', handlers.portfolios.Handler),
            URLSpec(r'/portfolios/new', handlers.portfolios.API_handler),

            URLSpec(r'/portfolio-edit-transactions', handlers.portfolios.Edit_transactions_handler),
            URLSpec(r'/portfolio-edit-crontab', handlers.portfolios.Edit_crontab_handler),
            URLSpec(r'/portfolio-new-cron', handlers.portfolios.New_cron_handler),

            URLSpec(r'/reports/(.*)', web.StaticFileHandler, {'path': config['report']['path']}),

        ]
        engine = create_engine(config['database']['url'], echo=False)
        web.Application.__init__(self, urls, **settings)

def main():
    Logger.set_logger('web.log')
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(config['web']['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()