from flask import current_app, request, abort, Response, jsonify
from flask.views import MethodView
from flask.ext.login import current_user, login_user
from app import login_manager
from tools.login_manager import get_user_from_http_auth, get_user_from_token
from models import AuthToken
from base64 import b64encode
import logging

logger = logging.getLogger(__name__)


def hello():
    return "Hello Auth!"


class ApiLogin(MethodView):
    methods = ['POST', 'OPTIONS']

    def post(self):
        user = get_user_from_http_auth()
        if not user:
            logger.debug("no user returned: %s" % user)
            print "no user returned"
            abort(401)
        if not login_user(user):
            logger.debug("couldn't log user in: %s" % user)
            print "couldn't log user in"
            abort(401)
        token = AuthToken.create_token_for_user(user)
        base64_token = b64encode(token.token)
        resp = jsonify({'token': base64_token,
                        'newtoken': token.created,
                        'created': token.created,
                        'expires': token.expires})
        return resp


api_login = ApiLogin.as_view('api_login')


class ApiCheckToken(MethodView):
    methods = ['POST']

    def post(self):
        user = get_user_from_token()
        if not user:
            logger.debug("no user returned: %s" % user)
            print "no user returned"
            abort(401)
        if not login_user(user):
            logger.debug("couldn't log user in: %s" % user)
            print "couldn't log user in"
            abort(401)
        resp = jsonify({'valid': True})
        return resp

api_token_check = ApiCheckToken.as_view('api_token_check')
