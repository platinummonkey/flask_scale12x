from flask import request, _request_ctx_stack
from flask.ext.login import LoginManager, login_user
from flask import request
from werkzeug.utils import import_string

import logging
from base64 import b64decode


logger = logging.getLogger(__name__)


def decode_token(token):
    if not token or token == 'AA==':
        # no token supplied or null value
        return None
    otoken = token
    try:
        token = b64decode(token)
        return token
    except TypeError:
        logger.warn("Error Decrypting Token: %s" % otoken)
        return None


class TokenSessionLoginManager(LoginManager):
    """ LoginManager that supports reloading users from Tokens

    """
    def reload_user(self):
        # Add support for current_user and @login_required to support Token Authentication
        token_keys = ['TOKEN', 'HTTP_TOKEN']
        for token_key in token_keys:  # Iterate through possible keys
            if token_key in request.headers:
                #decode_token = import_string('auth.login_methods.decode_token')
                token = decode_token(request.headers.get(token_key))
                if token:  # we have acquired a properly decoded token, let's try to fetch the user
                    user = self.token_callback(token)
                    if user and login_user(user):
                        ctx = _request_ctx_stack.top
                        ctx.user = user
                        return

        super(TokenSessionLoginManager, self).reload_user()


def get_user_from_token():
    """
    Token Authentication, which is base64 encoded

    Clients should authenticate by passing the base64 encoded token key in
    the "TOKEN" HTTP header for example:

    TOKEN: YjBiM2EwNTUtODhmYy00Y2FlLWE2ZmMtOGI1MWI1NzMyMjk4

    NOTE: HTTP_ prefix works as well

    A temporary access token model that contains:

        * token -- The string identifying the plaintext token
        * user -- The user to which the token belongs
        * expires -- The DateTime to which the token expires
        * created -- The DateTime to which the token was created

    @returns: auth.models.User | None
    """

    from app import login_manager

    header_token_keys = ['TOKEN', 'HTTP_TOKEN']
    for header_token_key in header_token_keys:
        enc_token = request.headers.get(header_token_key, None)
        if enc_token:
            print "found encoded token %s on header %s" % (enc_token, header_token_key)
            break

    if not enc_token or enc_token == 'AA==':
        # no token supplied or null value
        print "no token supplied or null"
        return None

    token = decode_token(enc_token)
    print "decoded token: %s" % token

    if token:
        user = login_manager.token_callback(token)
        print "Got user: %s" % user
        return user

    return None


def get_user_from_http_auth():
    """
    Basic Auth with base64 encoded username/password fields

    Clients should authenticate by passing the base64 encoded email and
    password in the "USERNAME" and "PASSWORD" HTTP headers respectively.
    For Example::

      USERNAME: dGVzdHVzZXJAd2VsbGF3YXJlLnVz
      PASSWORD: TGludXggaXMgZm9yIGF3ZXNvbWUgcGVvcGxlLiBNYWNzIGFuZCBQQydzIGFyZSBmb3IgaWRpb3RzLg==

    NOTE: HTTP_ prefix works as well

    SIMPLE TEST: fire up runserver and in seperate terminal:
    for username: testuser@wellaware.us and password: testuser
     >>> curl -H "USERNAME: dGVzdHVzZXJAd2VsbGF3YXJlLnVz" \
     ...     -H "PASSWORD: TGludXggaXMgZm9yIGF3ZXNvbWUgcGVvcGxlLiBNYWNzIGFuZCBQQydzIGFyZSBmb3IgaWRpb3RzLg==" \
     ...     -d "" http://localhost:8000/api/auth/

    This will create a temporary Token for authorization for the set period of
    time (see login view). This Client should expect a plain-text token key as
    a response to the login. The Client is expected to base64 encode that token
    for future requests.

    @returns: auth.models.User | None
    """
    header_username_keys = ['USERNAME', 'HTTP_USERNAME']
    header_password_keys = ['PASSWORD', 'HTTP_PASSWORD']
    for hdr_u_key in header_username_keys:
        enc_username = request.headers.get(hdr_u_key, None)
        if enc_username:
            break
    for hdr_p_key in header_password_keys:
        enc_password = request.headers.get(hdr_p_key, None)
        if enc_password:
            break

    if (not enc_username or enc_username == 'AA==') or (not enc_password or enc_password == 'AA=='):
        logger.debug('No username or password')
        print "no username or password supplied"
        return None

    from auth.models import User

    try:
        username = b64decode(enc_username)
        password = b64decode(enc_password)
        logger.debug("Username: %s | Password: %s" % (username, password))
        user = User.get_by_username(username)
        print "Got User: %s" % user
        if not user:
            print "No such user"
            return None
        if not user.is_active or not user.check_password(password):
            print "User is not active or password check fail"
            return None
        print "user is good, sending back: %s, %s, %s" % (user.username, user.email, user.first_name)
        return user

    except User.DoesNotExist:
        logger.warn("No such user")
    except TypeError as e:  # base64 decoding problem
        logging.exception("Error decoding username and/or password")

    return None


def setup_login_manager(login_manager):
    from auth.models import AnonymousUser, User, AuthToken

    # Setup Anonymous User
    login_manager.anonymous_user = AnonymousUser

    # session protection
    login_manager.session_protection = 'strong'

    # login view
    #login_manager.login_view = 'auth.api_login'

    @login_manager.user_loader
    def load_user(userid):
        try:
            return User.get(userid)
        except Exception as e:
            logger.info("Error loading user %s: %s" % (userid, e))
            return None

    @login_manager.token_loader
    def load_user_by_token(token):
        """
        @param token: Token to lookup
            @type token: str
        @returns: auth.models.User | None
        """
        try:
            print "Trying to lookup token: %s" % token
            token = AuthToken.lookup_single(token=unicode(token))
            print "Received lookup: %s" % token
            if not token:
                logger.debug('No such token exists')
                print 'No such token exists'
                return None
            if token.isExpired():
                logger.info("Token has expired: %s" % token)
                print "Token has expired: %s" % token
                return None
            else:
                return token.get_user_from_token()
        except AuthToken.DoesNotExist:
            logger.info("No token found: %s" % token)
            print "No token found: %s" % token
            return None
    return login_manager
