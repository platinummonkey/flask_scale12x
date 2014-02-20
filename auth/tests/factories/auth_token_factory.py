from auth.models import AuthToken
from tools.ogm_factory import BulbsWrapperModelFactory, factory
from tools.dateutils import current_datetime, offset_token_current_datetime


class AuthTokenFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = AuthToken

    token = AuthToken.generate_key()
    device_type = factory.Iterator(['web', 'android', 'ios'])
    created = current_datetime()
    expires = offset_token_current_datetime()

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        token = super(AuthTokenFactory, cls)._create(target_class, *args, **kwargs)
        """ @type token: auth.models.AuthToken """
        # create relationship
        if 'user' in kwargs:
            """ @type kwargs['user']: auth.models.User"""
            token.apply_token_to_user(getattr(kwargs, 'user'), token)
        return token

__all__ = ['PermissionGroup', 'PermissionGroupFactory']