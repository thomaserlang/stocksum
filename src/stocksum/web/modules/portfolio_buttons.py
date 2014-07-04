from tornado import web

class Module(web.UIModule):

    def render(self, portfolio_id):
        return self.render_string(
            'portfolio_buttons.html',
            portfolio_id=portfolio_id,
        )