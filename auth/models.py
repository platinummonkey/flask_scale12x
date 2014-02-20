from tools.bulbs_wrapper import Node, Relationship
from bulbs.property import *
from tools.bulbs_extra_fields import *
from flask.ext.login import UserMixin, AnonymousUserMixin
from tools.dateutils import current_datetime, offset_token_current_datetime, gmt
from uuid import uuid4
import logging
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)


class AnonymousUser(AnonymousUserMixin):
    """ Anonymous User Model """

    username = u'Guest'
    email = None
    first_name = u'Guest'
    last_name = u''
    is_superuser = False
    is_wellaware_staff = False
    active = True
    date_joined = datetime.datetime(2013, 2, 1, tzinfo=gmt)

    def __init__(self):
        pass

    def get_id(self):
        return None

    @property
    def full_name(self):
        return u'Guest'

    @classmethod
    def create(cls):
        return cls()


class User(Node, UserMixin):
    """ User Model

    The representation of a user and their profile.
    """
    element_type = 'user'

    username = String(nullable=False, indexed=True, unique=True)
    email = Email(nullable=False, indexed=True, unique=True)
    password = String(nullable=True)
    first_name = String(nullable=False)
    last_name = String(nullable=False)
    is_superuser = Bool(default=False, nullable=False)
    is_wellaware_staff = Bool(default=False, nullable=False)
    active = Bool(default=True, nullable=False)
    date_joined = DateTimeGMT(default=current_datetime, nullable=False)

    def is_active(self):
        if isinstance(self.active, bool):
            return self.active
        return False

    def get_id(self):
        try:
            return unicode(self.eid)
        except:
            raise Exception("User not instantiated")

    def check_password(self, password):
        """ Check password for validity

        We use Werkzeug's password checking algorithm
        """
        logging.debug("checking password %s against %s" % (password, self.password))
        return check_password_hash(self.password, password)

    @classmethod
    def encrypt_password(cls, password):
        """ Encrypt a password before saving it to the database

        We use Werkzeug's password encryption algorithms, default is pbkdf2:sha1, length 8
        """
        return generate_password_hash(password)

    @classmethod
    def get_by_email(cls, email):
        return cls.lookup_single(email=email)

    @classmethod
    def get_by_username(cls, username):
        return cls.lookup_single(username=username)

    @property
    def full_name(self):
        return u'%s %s' % (self.first_name.capitalize() + self.last_name.capitalize())


class UserGroupRelationship(Relationship):
    label = "is_member_of_group"

    since = DateTimeGMT(default=current_datetime, nullable=False)


class Group(Node):
    """ Group Model

    The representation of a group
    """

    element_type = 'group'

    name = String(nullable=False, indexed=True)
    description = String(nullable=True)


class Permission(Relationship):
    """ Permission Relationship between a Group or User and an another Node """
    label = 'has_permission'

    target_properties = List(nullable=True)  # if this is empty it is assumed this permission applies to the entire Node
                                             # otherwise only apply to the permissions to the selected properties
    can_view = Bool(default=True, nullable=False)
    can_edit = Bool(default=False, nullable=False)
    can_update = Bool(default=False, nullable=False)
    can_create = Bool(default=False, nullable=False)
    can_destroy = Bool(default=False, nullable=False)


class PermissionGroup(Node):
    """ Permission Group

    Use this to aggregate permissions across a whole group of things

    These should only have Permissions edges coming in and out of this Node.

    Users/Groups -(n)--Permission--(1)-> PermissionGroup -(1)--Permissions--(n)-> Things
    This still allows for direct individual permissions, where the individual user permissions override everything. (ie.
    if an admin removes the ability for Bob to see Thing#100 this is possible.

    ie. This is still possible and overrides PermissionGroups.
    User --Permission--> Asset

    Think of Permission Groups as an equivalent of User Group permissions for assets
    """
    element_type = 'permission_group'

    name = String(nullable=False, indexed=True)

    target_properties = List(nullable=True)  # if this is empty it is assumed this permission applies to the entire Node
                                             # otherwise only apply to the permissions to the selected properties

    enforce_permission_changes = Bool(default=True, nullable=False)

    can_view = Bool(default=True, nullable=False)
    can_edit = Bool(default=False, nullable=False)
    can_update = Bool(default=False, nullable=False)
    can_create = Bool(default=False, nullable=False)
    can_destroy = Bool(default=False, nullable=False)


class AuthRelationship(Relationship):
    """ Link from Auth Token to User (ManyToOne) """

    label = 'auth_token_registered_to'


class AuthToken(Node):
    """ Active login token for a given User on their specific device """

    element_type = 'auth_token'

    token = String(nullable=False, indexed=True, unique=True)
    device_type = String(nullable=True)
    created = DateTimeGMT(default=current_datetime, nullable=False)
    expires = DateTimeGMT(default=offset_token_current_datetime, nullable=False, indexed=True)

    @classmethod
    def generate_key(cls):
        """ Unique Key Generation

        Currently this uses the UUID4 algorithm, we may consider a different algorithm.
        """
        return uuid4().hex

    def baIsExpired(self):
        """ Checks if AuthToken has expired based on overlap conditions for basic auth """
        if self.expires <= current_datetime() + datetime.timedelta(hours=1):
            logger.warn("Expires between now and +1hr: %s, Current: %s" % (self.expireDate, current_datetime()))
            return True
        return False

    def isExpired(self):
        print "Current Datetime: %s, %s" % (current_datetime(), current_datetime().tzinfo)
        print "Expires: %s, %s" % (self.expires, self.expires.tzinfo)
        if current_datetime() >= self.expires:
            logger.info('Expired token: %s, Current: %s' % (self.expires, current_datetime()))
            return True
        return False

    def expire(self):
        #self.outE().delete(self.outE()._id)  # Delete edge first
        ## ^- Unnecessary titan will auto-remove these kinds of edges -^
        self.delete(self._id)  # delete node

    def expiration_maintenance_check(self):
        """ Method intended for a routine cleanup task to call.

        TODO: make this a groovy method
        """
        if self.isExpired():
            self.expire()

    @classmethod
    def apply_token_to_user(cls, user, token):
        return AuthRelationship.create(token, user)

    @classmethod
    def create_token_for_user(cls, user, device_type=None):
        """

        @param user: User node
            @type user: User
        @return: AuthToken
        """
        # create token first, then edge #TODO put this into a groovy file, so it's transactional
        auth_token = cls._PROXY.create(token=cls.generate_key(), device_type=device_type)
        auth_edge = cls.apply_token_to_user(user, auth_token)
        return auth_token

    def get_user_from_token(self):
        """ Get the associated user """
        print "Trying to get user from self token %s" % self.token
        user = self.outV().next()
        print "Got user: %s" % user
        return user
