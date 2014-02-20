from flask.ext.testing import TestCase


class FlaskClientBaseTestCase(TestCase):

    def create_app(self):
        from app import app
        try:
            from tools.apps import installed_apps_loader
            installed_apps_loader(app, app.config['INSTALLED_APPS'])
        except:
            pass
        app.testing = True
        #app.config['TESTING'] = True
        #app.test_client()
        self.client = app.test_client()
        return app
