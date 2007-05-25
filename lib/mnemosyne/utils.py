import os
import email, email.Message, email.Header

class Message(email.Message.Message):
    """Non-broken version of email's Message class. Returns unicode headers
    when necessary and raises KeyError when appropriate."""

    def __getitem__(self, item):
        header = email.Message.Message.__getitem__(self, item)
        if not header:
            raise KeyError
        def actually_decode(s, e):
            if e: return s.decode(e)
            else: return s
        parts = email.Header.decode_header(header)
        parts = [actually_decode(s, encoding) for s, encoding in parts]
        return ' '.join(parts)

    def get_body(self):
        """Returns the message payload with any signature stripped."""

        s = self.get_payload(decode=True)
        try:
            return s[:s.rindex('-- \n')]
        except ValueError:
            return s

class UniqueDict(dict):
    """A read-only dict which munges its values so that they are unique. If an
    existing key has the value 'foo', attempting to set another key to 'foo'
    will cause it to become 'foo-1', then 'foo-2', etc. These numberings are
    stable as long as each key is assigned to in the same order; attempting to
    set an existing key will cause a ValueError. """

    def __getitem__(self, k):
        k, i = dict.__getitem__(self, k)
        if i: return '%s-%d' % (k, i)
        else: return k

    def __setitem__(self, k, v):
        if k in self: raise ValueError
        n = len([x for x, y in self.iteritems() if y[0] == v])
        dict.__setitem__(self, k, (v, n))

    # Yes, we must. Le sigh.
    def setdefault(self, key, failobj=None):
        if not self.has_key(key): self[key] = failobj
        return self[key]

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
        return '-'.join(words)
    except AttributeError:
        return None

def get_conf(s):
    return os.path.expanduser('~/.mnemosyne/%s' % s)
