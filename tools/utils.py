from flask import abort, url_for
from flask.ext.login import current_user


def get_setting(key, default=None):
    from app import app
    try:
        return app.config[key]
    except KeyError:
        return default


def get_model(module, model_name):
    """ Attempts to return a known registered model """
    from app import app
    try:
        return getattr(app.g, '_APP_MODELS', {})[module][model_name]
    except KeyError:
        return None
    except AttributeError as e:
        raise Exception("Error getting model from app models cache: %s.%s" % (module, model_name))


def get_object_or_404(model, *args, **kwargs):
    obj_list = model.lookup(**kwargs)
    if not obj_list or len(obj_list) > 1:
        abort(404)
    return obj_list


def get_list_or_404(model, *args, **kwargs):
    """ Obtain a list of objects or 404 if none are available

    @param model:
        @type model: tools.bulbs_wrapper.Node | tools.bulbs_wrapper.Relationship
    @return: list[T]
    """
    obj_list = model.lookup(**kwargs)
    if not obj_list:
        abort(404)
    return obj_list


def get_403_or_none(user, perms, obj=None, login_url=None, redirect_field_name=None, return_403=False,
                    accept_global_perms=False):
    """ Check Permissions for a given object, 403 if they don't have permission to view that object, otherwise return
    the normal view response

    @param user:
        @type user: auth.models.User
    @param perms: Permissions required to view the object
        @type perms: str
    @param obj:  Object in question that permissions should surround
        @type obj: tools.bulbs_wrapper.Node
    @param login_url: Login url
        @type login_url: str
    @param redirect_field_name: Redirect field name
        @type redirect_field_name: str
    @param return_403: Return 403 response if error
        @type return_403: bool
    @param accept_global_perms: Accept global permissions?
        @type accept_global_perms: bool
    @raise: Exception
    @return: None
    """
    from app import app

    login_url = login_url or app.config.get('LOGIN_URL', '/login')
    redirect_field_name = redirect_field_name or app.config.get('REDIRECT_FIELD_NAME', 'next')

    # Handles both original and with object provided permission check
    # as ``obj`` defaults to None

    has_permissions = False
    # global perms check first (if accept_global_perms)
    if accept_global_perms:
        has_permissions = all(user.has_perm(perm) for perm in perms)
    # if still no permission granted, try obj perms
    if not has_permissions:
        has_permissions = all(user.has_perm(perm, obj) for perm in perms)

    if not has_permissions:
        if return_403:
            abort(403)
        abort(403)


def get_url(ep_url):
    try:
        return url_for(ep_url)
    except:
        return ep_url


def config_value(key, application=None, default=None):
    """ Get a configuration value

    @param key: The configuration key
        @type key: str
    @param application: The application context
        @type application: flask.Flask
    @param default: Default value if not found
    @return: object
    """
    from app import app
    application = application or app
    return application.config.get(key, default)
