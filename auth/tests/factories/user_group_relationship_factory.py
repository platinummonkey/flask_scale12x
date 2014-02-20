from auth.models import UserGroupRelationship
from tools.ogm_factory import BulbsWrapperModelFactory, factory
from tools.dateutils import current_datetime


class UserGroupRelationshipFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = UserGroupRelationship

    since = current_datetime()

__all__ = ['UserGroupRelationship', 'UserGroupRelationshipFactory']