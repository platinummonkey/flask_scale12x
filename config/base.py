""" Base Flask-Environment configuration on which all environments subclass

See http://pythonhosted.org/Flask-Environments/ for more information.
"""

from bulbs.titan import Graph, Config

class BaseConfig(object):
   DEBUG = True
   TESTING = True
   HOST = '0.0.0.0'
   PORT = 8000
   ADMINS = frozenset(['webmaster@example.com'])
   INSTALLED_APPS = (
       '',
       ('auth', '/auth')
   )
   DATABASE = Graph()
   LOGIN_URL='/login'
   SESSION_SECRET_KEY = 'base_null_key'
