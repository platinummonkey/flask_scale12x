import logging
from flask import _request_ctx_stack, redirect, abort
from flask.ext.login import current_user, login_required
from functools import wraps
from tools.utils import url_for
from app import login_manager
from tools.login_manager import get_user_from_token, get_user_from_http_auth

logger = logging.getLogger(__name__)


def auth_token_required(fn):
    """ Decorator that protects endpoints using token authentication. The token should be added to the request by the
    client by using a request header named that of the configuration value of `AUTH_TOKEN_KEY`
    """

    @wraps(fn)
    def decorated(*args, **kwargs):
        if get_user_from_token():
            return fn(*args, **kwargs)
        abort(403)
    return decorated


def http_auth_required(fn):
    """ Decorator that protects endpoints by using Basic HTTP authenication. The authorization fields should be added to
    the request by the client by using a request header named that of the configuration value of `AUTH_TOKEN_USERNAME` and
    `AUTH_TOKEN_PASSWORD`
    """
    @wraps(fn)
    def decorated(*args, **kwargs):
        if get_user_from_http_auth():
            return fn(*args, **kwargs)
        abort(403)
    return decorated


def session_auth_required(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated() and current_user.is_active():
            return fn(*args, **kwargs)
        abort(403)
    return decorated


def anonymous_user_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated():
            return redirect(url_for(login_manager.login_view))
        return f(*args, **kwargs)
    return wrapper

__all__ = ['http_auth_required', 'auth_token_required', 'session_auth_required', 'anonymous_user_required',
           'login_required']
