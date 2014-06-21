from tornado import web
from stocksum.web.decorators import new_session
from stocksum.web import models

class Module(web.UIModule):

    def render(self):
        with new_session() as session:
            portfolios = session.query(models.Portfolio).filter(
                models.Portfolio.user_id == self.current_user['id']
            ).all()
            return self.render_string(
                'portfolios_menu.html',
                portfolios=portfolios,
            )