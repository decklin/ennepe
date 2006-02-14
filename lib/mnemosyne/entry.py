import os
import time
import docutils.core
import email, email.Utils

import utils

class BaseEntry:
    """Base class for all entries. Initialized with an open file object, so it
    may be passed to maildir.Maildir as a factory class. Parses the file's
    contents as a Message object, setting a date attribute from the parsed
    date and an mtime attribute from the Maildir filename."""

    def __init__(self, fp):
        def fixdate(d):
            # For some bizarre reason, parsedate doesn't set wday/yday/isdst.
            return time.localtime(time.mktime(d))
        def getstamp(mpath):
            # djb says you're not supposed to do this. djb can bite me.
            stamp, id, host = os.path.split(mpath)[1].split('.')
            return int(stamp)

        self.msg = email.message_from_file(fp, utils.Message)
        self.date = fixdate(email.Utils.parsedate(self.msg['Date']))
        self.mtime = time.localtime(getstamp(fp.name))

    def __cmp__(self, other):
        if other:
            return cmp(time.mktime(self.date), time.mktime(other.date))
        else:
            return 1

    def _prop_content(self):
        """Read in the message's body, strip any signature, and format using
        reStructedText."""

        s = self.msg.get_payload(decode=True)
        if not s: return ''

        try: s = s[:s.rindex('-- \n')]
        except ValueError: pass

        parts = docutils.core.publish_parts(s, writer_name='html')
        body = parts['body']

        self.cache('content', body)
        return body

    byday = {}
    def _init_subject(self):
        """Get the contents of the Subject: header and a cleaned, uniq'd
        version of same."""

        try:
            subject = self.msg['Subject']
            cleaned = utils.clean(subject, 3)
        except KeyError:
            subject = ''
            cleaned = 'entry'

        # Grab the namespace for the day of this entry
        day = self.byday.setdefault(self.date[0:3], utils.UniqueDict())

        slug = day.setdefault(hash(self.msg), cleaned)
        return utils.cook(subject, slug)

    def _init_id(self):
        """Get the Message-ID and a globally unique tag: URL based on it, for
        use in feeds."""

        try:
            id = self.msg['Message-Id'][1:-1]
            local, host = id.split('@')
            date = time.strftime('%Y-%m-%d', self.date)
            return utils.cook(id, 'tag:%s,%s:%s' % (host, date, local))
        except KeyError:
            return ''

    def _init_author(self):
        """Get the real name portion of the From: address."""
        author, addr = email.Utils.parseaddr(self.msg.get('From'))
        return utils.cook(author, utils.clean(author))

    def _init_email(self):
        """Get the author's email address and a trivially spam-protected
        version of same."""
        try:
            author, addr = email.Utils.parseaddr(self.msg['From'])
            cleaned = addr.replace('@', ' at ')
            cleaned = cleaned.replace('.', ' dot ')
            cleaned = cleaned.replace('-', ' dash ')
            return utils.cook(addr, cleaned)
        except KeyError:
            return ''

    def _init_tags(self):
        """Get a list of tags from the comma-delimited X-Tags: header."""
        try:
            tags = [t.strip() for t in self.msg['X-Tags'].split(',')]
            return [utils.cook(t, utils.clean(t)) for t in tags]
        except KeyError:
            return []

    def _init_year(self):
        """Get the year from the Date: header."""
        return utils.cook(self.date[0], time.strftime('%Y', self.date))

    def _init_month(self):
        """Get the month from the Date: header."""
        return utils.cook(self.date[1], time.strftime('%m', self.date))

    def _init_day(self):
        """Get the day of the month from the Date: header."""
        return utils.cook(self.date[2], time.strftime('%d', self.date))

class Entry(BaseEntry):
    """Actual entry class. Will search the user-provided mixin class and then
    BaseEntry for methods of the form _init_*, and set the appropriate
    attribute on initialization, and also search for methods of the form
    _prop_* to provide properties to be evaluated on demand."""

    def __init__(self, fp):
        for _class in self.__class__.__bases__:
            try: _class.__init__(self, fp)
            except AttributeError: pass

            for k, v in _class.__dict__.iteritems():
                if k.startswith('_init_'):
                    setattr(self, k[6:], v(self))

    attrcache = {}
    def __getattr__(self, a):
        cache = self.attrcache.setdefault(hash(self.msg), {})
        try:
            return cache[a]
        except KeyError:
            for _class in self.__class__.__bases__:
                try:
                    method = getattr(_class, '_prop_'+a)
                    return cache.setdefault(a, method(self))
                except AttributeError:
                    pass
        return getattr(BaseEntry, a)

    def cache(self, attr, val):
        cache = self.attrcache.setdefault(hash(self.msg), {})
        cache[attr] = val
