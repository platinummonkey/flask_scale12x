#from auth.models import Permission, User, AnonymousUser, Group, UserGroupRelationship, PermissionGroup
#from tools.bulbs_wrapper import Node


def create_permission_for(principal, need):
    """ Adds a permission for a given Principal

    @param principal: Principal Object
        @type principal: auth.models.User | auth.models.Group | auth.models.PermissionGroup
    @param need:
        @type need: Node
    @return: None
    """
    pass  # TODO


def remove_permission_for(principal, need):
    """ Removes a permission for a given Principal

    @param principal: Principal Object
        @type principal: auth.models.User | auth.models.Group | auth.models.PermissionGroup
    @param need:
        @type need: Node
    @return: None
    """
    pass  # TODO


def create_permission_group(assets, can_view=True, can_edit=False, can_update=False,
                            can_create=False, can_destroy=False, enforce_permission_changes=True,
                            target_properties=None):
    """ Create a PermissionGroup for a collection of assets

    @param assets: List of assets that need permissions
        @type assets: list[tools.bulbs_wrapper.Node]
    @param can_view: Can View Assets in this group, Default: True
        @type can_view: Bool
    @param can_edit: Can Edit Assets in this group, Default: False
        @type can_edit: Bool
    @param can_update: Can Update Assets in this group, Default: False
        @type can_update: Bool
    @param can_create: Can Create Assets in this group, Default: False
        @type can_create: Bool
    @param can_destroy: Can Destroy Assets in this group, Default: False
        @type can_destroy: Bool
    @param enforce_permission_changes: Enforce Permission changes on the group to affect all edges, Default: True
        @type enforce_permission_changes: Bool
    @param target_properties: if this is empty it is assumed this permission applies to the entire Node
                              otherwise only apply to the permissions to the selected properties
        @type target_properties: list[str]
    @return:
    """
    pass  # TODO
