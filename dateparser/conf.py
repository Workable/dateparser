# -*- coding: utf-8 -*-
import hashlib
from pkgutil import get_data
from itertools import chain
from functools import wraps
import six

from yaml import load as load_yaml

from .utils import registry


@registry
class Settings(object):
    """Control and configure default parsing behavior of dateparser.
    Currently, supported settings are:
    - `PREFER_DATES_FROM`: defaults to `current_period`. Options are `future` or `past`.
    - `SUPPORT_BEFORE_COMMON_ERA`: defaults to `False`.
    - `PREFER_DAY_OF_MONTH`: defaults to `current`. Could be `first` and `last` day of month.
    - `SKIP_TOKENS`: defaults to `['t']`. Can be any string.
    """

    _default = True
    _yaml_data = None

    def __init__(self, **kwargs):
        self._updateall(
            chain(self._get_settings_from_yaml().items(),
                  kwargs.items())
        )

    @classmethod
    def get_key(cls, *args, **kwargs):
        if not args and not kwargs:
            return 'default'

        keys = sorted(['%s-%s' % (key, str(kwargs[key])) for key in kwargs])
        return hashlib.md5(''.join(keys)).hexdigest()

    @classmethod
    def _get_settings_from_yaml(cls):
        if not cls._yaml_data:
            data = get_data('data', 'settings.yaml')
            cls._yaml_data = load_yaml(data).pop('settings', {})
        return cls._yaml_data

    def _updateall(self, iterable):
        for key, value in iterable:
            setattr(self, key, value)

    def replace(self, **kwds):
        for x in six.iterkeys(self._get_settings_from_yaml()):
            kwds.setdefault(x, getattr(self, x))

        kwds['_default'] = False

        return self.__class__(**kwds)


settings = Settings()


def apply_settings(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs['settings'] = kwargs.get('settings', settings)

        if kwargs['settings'] is None:
            kwargs['settings'] = settings

        if isinstance(kwargs['settings'], dict):
            kwargs['settings'] = settings.replace(**kwargs['settings'])

        if not isinstance(kwargs['settings'], Settings):
            raise TypeError(
                "settings can only be either dict or instance of Settings class")

        return f(*args, **kwargs)
    return wrapper
