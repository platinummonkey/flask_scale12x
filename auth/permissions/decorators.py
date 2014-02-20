from functools import wraps
from tools.utils import get_setting, get_model, get_object_or_404, get_403_or_none
from tools.bulbs_wrapper import Node, Relationship
from tools.constants import basestring
from flask.ext.login import current_user

## THIS IS A TODO item for the viewer. Untested, but the point is made.


class PermissionError(Exception):
    pass

## code originally developed by django-guardian, utilizes to minimize code changes between current codebase
# https://github.com/lukaszb/django-guardian/blob/devel/guardian/decorators.py
## LICENSE ASSOCIATED
#Copyright (c) 2010-2013 Lukasz Balcerzak <lukaszbalcerzak@gmail.com>
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#* Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#* Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def permission_required(perm, lookup_variables=None, **kwargs):
    """
    Decorator for views that checks whether a user has a particular permission enabled.

    Optionally, instances for which check should be made may be passed as an second argument or as a tuple parameters
    same as those passed to ``get_object_or_404`` but must be provided as pairs of strings. This way decorator can fetch
    i.e. ``User`` instance based on performed request and check permissions on it (without this, one would need to fetch
    user instance at view's logic and check permission inside a view).

    @param login_url: if denied, user would be redirected to location set by this parameter.
        Defaults to ``django.conf.settings.LOGIN_URL``.
    @param redirect_field_name: name of the parameter passed if redirected.
        Defaults to :setting:`REDIRECT_FIELD_NAME`.
    @param return_403: if set to ``True`` then instead of redirecting to the login page, response with status code 403
        is returned (``HttpResponseForbidden`` instance or rendered template - see
        :setting:`PERMISSION_RENDER_403`). Defaults to ``False``.
    @param accept_global_perms: if set to ``True``, then *object level permission* would be required **only if user
        does NOT have global permission** for target *model*. If turned on, makes this decorator like an extension over
        standard ``django.contrib.admin.decorators.permission_required`` as it would check for global permissions first.
        Defaults to ``False``.


    Examples::

        >>> @permission_required('auth.change_user', return_403=True)
        ... def my_view(request):
        ...   return HttpResponse('Hello')

        >>> @permission_required('auth.change_user', (User, 'username', 'username'))
        ... def my_view(request, username):

        auth.change_user permission would be checked based on given
        'username'. If view's parameter would be named ``name``, we would
        rather use following decorator::

        >>> @permission_required('auth.change_user', (User, 'username', 'name'))

        >>>     user = get_object_or_404(User, username=username)
        ...     return user.get_absolute_url()

    >>> @permission_required('auth.change_user',
    ...    (User, 'username', 'username', 'groups__name', 'group_name'))
    ... def my_view(request, username, group_name):
    ...     '''
    ...     Similar to the above example, here however we also make sure that
    ...     one of user's group is named same as request's ``group_name`` param.
    ...     '''
    ...     user = get_object_or_404(User, username=username,
    ...     group__name=group_name)
    ...     return user.get_absolute_url()

    """
    login_url = kwargs.pop('login_url', get_setting('LOGIN_URL', '/'))
    redirect_field_name = kwargs.pop('redirect_field_name', get_setting('REDIRECT_FIELD_NAME', 'next'))
    return_403 = kwargs.pop('return_403', False)
    accept_global_perms = kwargs.pop('accept_global_perms', False)

    # Check if perm is given as string in order not to decorate
    # view function itself which makes debugging harder
    if not isinstance(perm, basestring):
        raise PermissionError("First argument must be in format: "
                              "'app_label.codename' or a callable which return similar string'")

    def decorator(view_func):
        def _wrapped_view(*args, **kwargs):
            # if more than one parameter is passed to the decorator we try to
            # fetch object for which check would be made
            obj = None
            if lookup_variables:
                model, lookups = lookup_variables[0], lookup_variables[1:]
                # Parse model
                if isinstance(model, basestring):
                    splitted = model.split('.')
                    if len(splitted) != 2:
                        raise PermissionError("If model should be looked up from string it needs format:"
                                              "'app_label.ModelClass'")
                    model = get_model(*splitted)
                elif issubclass(model.__class__, (Node, Relationship)):
                    pass
                else:
                    raise PermissionError("First lookup argument must always be a model, string pointing at app/model "
                                          "or queryset. Given: %s (type: %s)" % (model, type(model)))
                # Parse lookups
                if len(lookups) % 2 != 0:
                    raise PermissionError("Lookup variables must be provided as pairs of lookup_string and view_arg")
                lookup_dict = {}
                for lookup, view_arg in zip(lookups[::2], lookups[1::2]):
                    if view_arg not in kwargs:
                        raise PermissionError("Argument %s was not passed into view function" % view_arg)
                    lookup_dict[lookup] = kwargs[view_arg]
                obj = get_object_or_404(model, **lookup_dict)

            response = get_403_or_none(user=current_user,
                                       perms=[perm],
                                       obj=obj,
                                       login_url=login_url,
                                       redirect_field_name=redirect_field_name,
                                       return_403=return_403,
                                       accept_global_perms=accept_global_perms)
            if response:
                return response
            return view_func(*args, **kwargs)
        return wraps(view_func)(_wrapped_view)
    return decorator


def permission_required_or_403(perm, *args, **kwargs):
    """
    Simple wrapper for permission_required decorator.

    Standard permission_required decorator redirects user to login page in case permission check failed.
    This decorator may be used to return HttpResponseForbidden (status 403) instead of redirection.

    The only difference between ``permission_required`` decorator is that this one always set ``return_403``
    parameter to ``True``.

    @param perm: Permission required
        @type perm: str
    @return: permission_required[perm, args, kwargs]
    """
    kwargs['return_403'] = True
    return permission_required(perm, *args, **kwargs)
