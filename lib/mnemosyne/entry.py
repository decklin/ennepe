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
            stamp, id, host = os.path.split(mpath)[1].split('.', 2)
            return int(stamp)

        self.msg = email.message_from_file(fp, utils.Message)
        self.date = fixdate(email.Utils.parsedate(self.msg['Date']))
        self.mtime = time.localtime(getstamp(fp.name))

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
            cleaned = utils.clean(subject, 3)
        except KeyError:
            subject = ''
            cleaned = 'entry'

        # Grab the namespace for the day of this entry
        day = self.byday.setdefault(self.date[0:3], utils.UniqueDict())

        slug = day.setdefault(hash(self.msg), cleaned)
        return utils.cook(subject, slug)

    def get_id(self):
        """Get the Message-ID and a globally unique tag: URL based on it, for
        use in feeds."""

        try:
            id = self.msg['Message-Id'][1:-1]
            local, host = id.split('@')
            date = time.strftime('%Y-%m-%d', self.date)
            return utils.cook(id, 'tag:%s,%s:%s' % (host, date, local))
        except KeyError:
            return ''

    def get_author(self):
        """Get the real name portion of the From: address."""
        author, addr = email.Utils.parseaddr(self.msg.get('From'))
        return utils.cook(author, utils.clean(author))

    def get_email(self):
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

    def get_tags(self):
        """Get a list of tags from the comma-delimited X-Tags: header."""
        try:
            tags = [t.strip() for t in self.msg['X-Tags'].split(',')]
            return [utils.cook(t, utils.clean(t)) for t in tags]
        except KeyError:
            return []

    def get_year(self):
        """Extract the year from the Date: header."""
        return utils.cook(self.date[0], time.strftime('%Y', self.date))

    def get_month(self):
        """Extract the month from the Date: header."""
        return utils.cook(self.date[1], time.strftime('%m', self.date))

    def get_day(self):
        """Extract the day of the month from the Date: header."""
        return utils.cook(self.date[2], time.strftime('%d', self.date))

class Entry(BaseEntry):
    """Actual entry class. To look up an attribute, will search the
    user-provided mixin classes and then BaseEntry for methods of the
    form get_*, caching the results (we assume that values are
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
                    return self.cache.setdefault(attr, method(self))
                except AttributeError:
                    pass
            else:
                raise AttributeError("Entry has no attribute '%s'" % attr)
