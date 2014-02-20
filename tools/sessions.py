from flask import Flask
from flask.ext.cache import Cache
from werkzeug.contrib.sessions import SessionStore
from flask import json


class CachedStore(SessionStore):

    def __init__(self, app, session_cache_config=None, app_cache_config=None):
        SessionStore.__init__(self)
        # check if app cache config exists, otherwise use the same as cache_config
        if app_cache_config and not session_cache_config:
            self._app_cache_client = Cache(config=app_cache_config)
            self._session_cache_client = Cache(config=app_cache_config)
        elif app_cache_config and session_cache_config:
            self._app_cache_client = Cache(config=app_cache_config)
            self._session_cache_client = Cache(config=session_cache_config)
        elif not app_cache_config and session_cache_config:
            self._app_cache_client = Cache(config=session_cache_config)
            self._session_cache_client = Cache(config=session_cache_config)
        else:
            self._app_cache_client = self._session_cache_client = Cache()
        self._app_cache_client.init_app(app)
        #self._session_cache_client.init_app(app)
        # now set the app config to contain the cache
        app.config['_session_cache'] = self._session_cache_client
        app.config['_app_cache'] = self._app_cache_client

    def save(self, session):
        key = self._get_memcache_key(session.sid)
        data = json.dumps(dict(session))
        print "{0}:{1}".format(key, data)
        self._cache_client.set(key, data)

    def delete(self, session):
        key = self._get_memcache_key(session.sid)
        self._memcache_client.delete(key)

    def get(self, sid):
        key = self._get_memcache_key(sid)
        data = self._memcache_client.get(key)
        if data is not None:
           session = json.loads(data)
        else:
            session = {}
        return self.session_class(session, sid, False)

    def _get_memcache_key(self, sid):
        if isinstance(sid, unicode):
            sid = sid.encode('utf-8')
        return sid


class SessionMixin(object):

    __slots__ = ('session_key', 'session_store')

    def open_session(self, request):
        sid = request.cookies.get(self.session_key, None)
        if sid is None:
            return self.session_store.new()
        else:
            return self.session_store.get(sid)

    def save_session(self, session, response):
        if session.should_save:
            self.session_store.save(session)
            response.set_cookie(self.session_key, session.sid)
        return response


class CachedFlask(SessionMixin, Flask):
    """ Use this as the Flask Core to enabled cached sessions

    app = MyFlask(__name__)
    app.session_key = '_my_super_secret_session_key'
    app.session_store = CachedSessionStore(app, cache_config={})
    """
    pass


def setup_sessioned_app(app, session_key, session_cache_config=None, app_cache_config=None, debug=False):
    assert issubclass(app.__class__, CachedFlask), "Must be a subclass of CachedFlask"
    app.session_key = session_key
    if not debug:
        app.session_store = CachedStore(app=app,
                                        session_cache_config=session_cache_config,
                                        app_cache_config=app_cache_config)
    else:
        #app.set_default_session()
        app.session_store = SessionStore()
