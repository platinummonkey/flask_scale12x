from factories.user_factory import UserFactory, User
from factories.auth_token_factory import AuthToken
from base64 import b64encode
from nose.plugins.attrib import attr
from tools.client_test_case import FlaskClientBaseTestCase
import logging

logger = logging.getLogger(__name__)


@attr('unit', 'api_auth')
class TestAPIAuthenticationTestCase(FlaskClientBaseTestCase):

    def setUp(self):
        #self.tearDown()
        self.user = UserFactory.create(username='bob@wellaware.us',
                                       email='bob@wellaware.us',
                                       password=UserFactory.FACTORY_FOR.encrypt_password('password123'))
        self.base_url = '/auth/api/auth/'

    def tearDown(self):
        user_element_proxy = User._GRAPH.user
        authtoken_element_proxy = AuthToken._GRAPH.authtoken
        # try to cleanup from previous test
        try:
            nodes = user_element_proxy.get_all()  # .index.lookup(name='test')
            if nodes:
                for p in nodes:
                    logger.debug("Got User (%s): %s" % (p.eid, p))
                    user_element_proxy.delete(p.eid)
                    logger.debug("Deleted User")
        except Exception as e:
            logger.exception(e)
        try:
            nodes = authtoken_element_proxy.get_all()
            if nodes:
                for n in nodes:
                    logger.debug("Got AuthToken (%s): %s" % (n.eid, n))
                    authtoken_element_proxy.delete(n.eid)
                    logger.debug("Deleted AuthToken")
        except Exception as e:
            logger.exception(e)

    def test_post_bad_http_auth(self):
        headers = [
            ('USERNAME', b64encode('bob@wellaware.us')),
            ('PASSWORD', b64encode('wrong_password'))
        ]
        data = ""
        response = self.client.post(self.base_url + 'login/', headers=headers, data=data)
        logger.debug("Got Response: %s" % repr(response))
        self.assert401(response)

    def test_post_good_http_auth(self):
        headers = [
            ('USERNAME', b64encode('bob@wellaware.us')),
            ('PASSWORD', b64encode('password123'))
        ]
        data = ""
        response = self.client.post(self.base_url + 'login/', headers=headers, data=data)
        self.assert200(response)
        logger.debug("Got Response: %s" % repr(response))
        self.assertIn('token', response.json)
        self.assertIn('newtoken', response.json)
        self.assertIn('created', response.json)
        self.assertIn('expires', response.json)

    def test_token_check_auth(self):
        token = AuthToken.create_token_for_user(self.user)
        base64_token = b64encode(token.token)
        logger.debug("Generated token: %s -> %s -> %s" % (token, token.token, base64_token))

        good_headers = [
            ('TOKEN', base64_token)
        ]

        bad_headers = [
            ('TOKEN', b64encode('badbadtoken'))
        ]

        data = ""

        # check good token auth
        response_good = self.client.post(self.base_url + 'tokencheck/', headers=good_headers, data=data)
        self.assert200(response_good)
        self.assertIn('valid', response_good.json)
        self.assertEqual(response_good.json['valid'], True)

        # check bad token auth
        response_bad = self.client.post(self.base_url + 'tokencheck/', headers=bad_headers, data=data)
        self.assert401(response_bad)
