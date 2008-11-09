"""Mnemosyne -- a static weblog generator."""

import os

__version__ = '0.12'
__author__ = 'Decklin Foster'
__email__ = 'decklin@red-bean.com'
__url__ = 'http://www.red-bean.com/decklin/mnemosyne/'

__all__ = ['muse', 'entry']

def get_conf(s):
    return os.path.expanduser('~/.mnemosyne/%s' % s)

def cook(obj, rep):
    """Create an object exactly like obj, except its repr() is rep. This
    lets us easily use repr() for URLs."""

    _class = type("Cooked", (type(obj),), {'__repr__': lambda self: rep})
    return _class(obj)

def clean(s, maxwords=None):
    """Split the given string into words, lowercase and strip all
    non-alphanumerics from them, and join them with '-'. If maxwords is
    given, limit the returned string to that many words. If the string
    is None, return None."""

    try:
        words = s.strip().lower().split()[:maxwords]
        words = [filter(lambda c: c.isalnum(), w) for w in words]
        return '-'.join(words) or '-'
    except AttributeError:
        return None

def dwim_iter(x):
    """Iterate over x, whatever that means. If it's a non-string
    sequence, this is the same as iter(). If it's a string type, or a
    non-sequence, create an iter that will yield that value once and
    then stop. If it's None, do nothing."""

    if not isinstance(x, basestring):
        try:
            return iter(x)
        except TypeError:
            pass

    if x != None:
        return iter((x,))
    else:
        return iter(())
