from auth.models import User, AnonymousUser
from tools.ogm_factory import BulbsWrapperModelFactory, factory
from tools.dateutils import current_datetime, datetime, gmt


class UserFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'Test User {0}'.format(n))
    email = factory.Sequence(lambda e: 'testuser{0}@wellaware.us'.format(e))
    password = User.encrypt_password('applesucks')
    first_name = 'Test'
    last_name = factory.Sequence(lambda n: 'User {0}'.format(n))
    is_superuser = False
    is_wellaware_staff = False
    active = True
    date_joined = current_datetime()


class AnonymousUserFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = AnonymousUser

    username = u'Guest'
    email = None
    first_name = u'Guest'
    last_name = u''
    is_superuser = False
    is_wellaware_staff = False
    active = True
    date_joined = datetime.datetime(2013, 2, 1, tzinfo=gmt)


__all__ = ['User', 'UserFactory', 'AnonymousUser', 'AnonymousUserFactory']