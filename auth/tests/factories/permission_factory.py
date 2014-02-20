from auth.models import Permission
from tools.ogm_factory import BulbsWrapperModelFactory, factory


class PermissionFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = Permission

    target_properties = factory.List(['asset', 'configuration', 'operations', 'gauger'])

    can_view = True
    can_edit = False
    can_update = False
    can_create = False
    can_destroy = False

__all__ = ['Permission', 'PermissionFactory']