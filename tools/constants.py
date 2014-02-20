
# Python 3
try:
    unicode = unicode
    basestring = basestring
    str = str
except NameError:
    basestring = unicode = str = str


__all__ = []