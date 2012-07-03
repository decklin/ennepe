import os
import time
import docutils.core
import email, email.Message, email.Header, email.Utils

from ennepe import cook, clean

class BaseEntry:
    """Base class for all entries. Initialized with an open file object, so it
    may be passed to maildir.Maildir as a factory class. Parses the file's
    contents as a Message object, setting a date attribute from the parsed
    date and an mtime attribute from the Maildir filename."""

    def __init__(self, fp):
        def fixdate(d):
            # For some bizarre reason, parsedate doesn't set wday/yday/isdst.
            return time.localtime(time.mktime(d))
        def getstamp(fp):
            # _ProxyFile is a disgusting kludge. I take no responsibility.
            try: path = fp.name # 2.4 or earlier
            except AttributeError: path = fp._file.name
            stamp, id, host = os.path.split(path)[1].split('.', 2)
            return int(stamp)

        self.msg = email.message_from_file(fp, Message)
        self.date = fixdate(email.Utils.parsedate(self.msg['Date']))
        self.mtime = time.localtime(getstamp(fp))

    def __cmp__(self, other):
        if other:
            return cmp(time.mktime(self.date), time.mktime(other.date))
        else:
            return 1

    def get_content(self):
        """Read in the message's body, strip any signature, and format using
        reStructedText."""

        s = self.msg.get_body()
        parts = docutils.core.publish_parts(s, writer_name='html')
        return parts['body']

    byday = {}
    def get_subject(self):
        """Get the contents of the Subject: header and a cleaned, uniq'd
        version of same."""

        try:
            subject = self.msg['Subject']
            cleaned = clean(subject, 3)
        except KeyError:
            subject = ''
            cleaned = 'entry'

        # Grab the namespace for the day of this entry
        day = self.byday.setdefault(self.date[0:3], UniqueDict())

        # This is not quite right. I think maybe it should be cook's
        # reponsibility to encode things.
        slug = day.setdefault(hash(self.msg), cleaned)
        return cook(subject, slug.encode('utf-8', 'replace'))

    def get_id(self):
        """Get the Message-ID and a globally unique tag: URL based on it, for
        use in feeds."""

        try:
            id = self.msg['Message-Id'][1:-1]
            local, host = id.split('@')
            date = time.strftime('%Y-%m-%d', self.date)
            return cook(id, 'tag:%s,%s:%s' % (host, date, local))
        except KeyError:
            return ''

    def get_author(self):
        """Get the real name portion of the From: address."""
        author, addr = email.Utils.parseaddr(self.msg.get('From'))
        return cook(author, clean(author))

    def get_email(self):
        """Get the author's email address and a trivially spam-protected
        version of same."""
        try:
            author, addr = email.Utils.parseaddr(self.msg['From'])
            cleaned = addr.replace('@', ' at ')
            cleaned = cleaned.replace('.', ' dot ')
            cleaned = cleaned.replace('-', ' dash ')
            return cook(addr, cleaned)
        except KeyError:
            return ''

    def get_tags(self):
        """Get a list of tags from the comma-delimited X-Tags: header."""
        try:
            tags = [t.strip() for t in self.msg['X-Tags'].split(',')]
            return [cook(t, clean(t)) for t in tags]
        except KeyError:
            return []

    def get_year(self):
        """Extract the year from the Date: header."""
        return cook(self.date[0], time.strftime('%Y', self.date))

    def get_month(self):
        """Extract the month from the Date: header."""
        return cook(self.date[1], time.strftime('%m', self.date))

    def get_day(self):
        """Extract the day of the month from the Date: header."""
        return cook(self.date[2], time.strftime('%d', self.date))

class Entry(BaseEntry):
    """Actual entry class. To look up an attribute, will search the
    user-provided mixin classes and then BaseEntry for methods of the
    form get_*, caching the results (it is assumed that values are
    referentially transparent)."""

    def __init__(self, fp):
        # might want to load this from disk, keyed on hash(self.msg)
        self.cache = {}
        for _class in self.__class__.__bases__:
            try: _class.__init__(self, fp)
            except AttributeError: pass

    def __getattr__(self, attr):
        try:
            return self.cache[attr]
        except KeyError:
            for _class in self.__class__.__bases__:
                try:
                    method = getattr(_class, 'get_'+attr)
                except AttributeError:
                    continue
                return self.cache.setdefault(attr, method(self))
            else:
                raise AttributeError("Entry has no attribute '%s'" % attr)

class Message(email.Message.Message):
    """Non-broken version of email's Message class. Returns unicode headers
    when necessary and raises KeyError when appropriate."""

    def __getitem__(self, item):
        header = email.Message.Message.__getitem__(self, item)
        if not header:
            raise KeyError
        def actually_decode(s, e):
            try: return s.decode(e)
            except: return s.decode('utf-8', 'replace')
        parts = email.Header.decode_header(header)
        parts = [actually_decode(s, encoding) for s, encoding in parts]
        return ' '.join(parts)

    def get_body(self):
        """Returns the message payload with any signature stripped."""
        body = self.get_payload(decode=True) or self.get_payload(decode=False)

        if isinstance(body, list):
            return ''.join([payload.get_body() for payload in body])
        else:
            return body[:body.rfind('-- \n')].decode('utf-8', 'replace')

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
