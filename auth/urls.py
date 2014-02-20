from flask import Blueprint
from tools.url_tools import url_configure, module_name

# Setup Blueprint
urls = Blueprint('accounts_url', module_name(__name__))

# define URLS here
url_configure(urls, 'auth',
    ('/', 'views.hello'),
    ('/api/auth/login/', 'views.api_login'),
    ('/api/auth/tokencheck/', 'views.api_token_check'),
    #('/api/auth/logout/', 'views.api_logout'),
)
