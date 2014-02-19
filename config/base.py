""" Base Flask-Environment configuration on which all environments subclass

See http://pythonhosted.org/Flask-Environments/ for more information.
"""

class BaseConfig(object):
   DEBUG = True
   TESTING = True
   HOST = '0.0.0.0'
   PORT = 8000
   ADMINS = frozenset(['webmaster@example.com'])

