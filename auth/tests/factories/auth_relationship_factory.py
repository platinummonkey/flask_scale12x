from auth.models import AuthRelationship
from tools.ogm_factory import BulbsWrapperModelFactory, factory


class AuthRelationshipFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = AuthRelationship


__all__ = ['AuthRelationship', 'AuthRelationshipFactory']