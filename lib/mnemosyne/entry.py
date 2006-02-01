import os
import time
from docutils.core import publish_string

import utils

class Entry(object):
    DOC_START = '<div class="document">'
    DOC_END = '</div>'
    RST_PREAMBLE = '.. role:: html(raw)\n   :format: html\n\n..\n\n'
    SIG_DELIM = '-- \n'

    def __init__(self, m):
        def fixdate(d):
            # For some bizarre reason, getdate doesn't set wday/yday/isdst...
            return time.localtime(time.mktime(d))
        def getstamp(maildirpath):
            stamp, id, host = os.path.split(maildirpath)[1].split('.')
            return int(stamp)
        def publish_html(s):
            try: s = s[:s.rindex(self.SIG_DELIM)]
            except ValueError: pass
            html = publish_string(self.RST_PREAMBLE + s, writer_name='html')
            start = html.find(self.DOC_START) + len(self.DOC_START)
            end = html.rfind(self.DOC_END)
            return html[start:end]

        # This violates abstraction by poking at m.fp
        self.date = fixdate(m.getdate('Date'))
        self.mtime = time.localtime(getstamp(m.fp.name))
        self.content = publish_html(m.fp.read())
        self.m = m

    def __getattribute__(self, a):
        try:
            method = object.__getattribute__(self, 'get_'+a)
            return method()
        except AttributeError:
            return object.__getattribute__(self, a)

    def __repr__(self):
        return '<Entry about "%s" dated %s>' % (self.subject,
            time.strftime('%Y-%m-%d %H:%M:%S', self.date))

    def __cmp__(self, other):
        return cmp(time.mktime(self.date), time.mktime(other.date))

    # And now attrs

    def get_author(self):
        author, email = self.m.getaddr('From')
        return author

    def get_email(self):
        author, email = self.m.getaddr('From')
        return email

    def get_id(self):
        try:
            id, host =  self.m['Message-Id'][1:-1].split('@')
            date = time.strftime('%Y-%m-%d', self.date)
            return 'tag:%s,%s:%s' % (host, date, id)
        except KeyError:
            return 'invalid:'

    def get_tags(self):
        try:
            return self.m['X-Mnemosyne-Tags'].split(',')
        except KeyError:
            return []

    def get_tag(self):
        # XXX: would prefer generator
        #for t in self.tags:
        #    yield utils.clean(t)
        return [utils.clean(t) for t in self.tags]

    def get_subject(self):
        try:
            return self.m['Subject']
        except KeyError:
            return 'Entry'

    def get_slug(self):
        s = utils.clean(self.subject, 3)
        return utils.unique(self.date[0:3], s, self.id)

    def get_year(self):
        return time.strftime('%Y', self.date)

    def get_month(self):
        return time.strftime('%m', self.date)

    def get_day(self):
        return time.strftime('%d', self.date)
