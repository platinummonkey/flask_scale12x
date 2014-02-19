from app import root_module
from flask import Blueprint
from tools.url_tools import url_configure

# Setup Blueprint
urls = Blueprint('root_url', root_module)

# define URLS here
url_configure(urls, '',
    ('/', 'views.index'),
)
