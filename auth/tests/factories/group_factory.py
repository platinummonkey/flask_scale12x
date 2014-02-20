from auth.models import Group
from tools.ogm_factory import BulbsWrapperModelFactory, factory


class GroupFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = Group

    name = factory.Sequence(lambda n: 'Test Group {0}'.format(n))
    description = factory.Sequence(lambda d: 'Some Group Description {0}'.format(d))

__all__ = ['Group', 'GroupFactory']