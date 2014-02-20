from auth.models import PermissionGroup
from tools.ogm_factory import BulbsWrapperModelFactory, factory


class PermissionGroupFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = PermissionGroup

    name = factory.Sequence(lambda n: 'Permission Group {0}'.format(n))

    target_properties = target_properties = factory.List(['asset', 'configuration', 'operations', 'gauger'])

    enforce_permission_changes = True

    can_view = True
    can_edit = False
    can_update = False
    can_create = False
    can_destroy = False

__all__ = ['PermissionGroup', 'PermissionGroupFactory']