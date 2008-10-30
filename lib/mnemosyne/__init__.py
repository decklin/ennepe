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
    """Create an object exactly like obj, except its repr() is rep. This will
    allow layouts to use the "cooked" rep (by convention, this is how we
    format stuff for URLs etc.) without caring how or when or why it was
    set."""

    _class = type("Cooked", (type(obj),), {'__repr__': lambda self: rep})
    return _class(obj)

def clean(s, maxwords=None):
    """Split the given string into words, lowercase and strip all
    non-alphanumerics from them, and join them with '-'. If maxwords is given,
    limit the returned string to that many words. If the string is None,
    return None."""

    try:
        words = s.strip().lower().split()[:maxwords]
        words = [filter(lambda c: c.isalnum(), w) for w in words]
        return '-'.join(words) or '-'
    except AttributeError:
        return None

def cheapiter(x):
    """DWIM-style iterator which, if given a sequence, will iterate over that
    sequence, unless it is a string type. For a string or any other atomic
    type, create an iterator which will return the given value once and then
    stop. Unless it's None. This is a horrible, horrible kludge."""

    try:
        if isinstance(x, basestring):
            return iter((x,))
        else:
            return iter(x)
    except TypeError:
        if x != None:
            return iter((x,))
        else:
            return iter(())
