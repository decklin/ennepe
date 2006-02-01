import os
import time
from docutils.core import publish_string

class BaseEntry:
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

    def __repr__(self):
        return '<Entry "%s" dated %s>' % (self.subject,
            time.strftime('%Y-%m-%d %H:%M:%S', self.date))

    def __cmp__(self, other):
        return cmp(time.mktime(self.date), time.mktime(other.date))

    def clean(self, s, maxwords=None):
        if s:
            words = s.strip().lower().split()
            if maxwords: words = words[:maxwords]
            words = [''.join([c for c in w if c.isalnum()]) for w in words]
            return '-'.join(words)

    namespaces = {}
    def uniq(self, ns, k, id):
        ns = self.namespaces.setdefault(ns, {})
        try:
            assert ns[k] == id
        except KeyError:
            ns[k] = id
        except AssertionError:
            while ns.has_key(k):
                components = k.split('-')
                try:
                    serial = int(components[-1])
                    components[-1] = str(serial + 1)
                    k = '-'.join(components)
                except ValueError:
                    k += '-1'
            ns[k] = id
        return k

class Mixin:
    def get_author(self):
        author = self.m.getaddr('From')[0]
        return author, self.clean(author)

    def get_email(self):
        email = self.m.getaddr('From')[1]
        return email, self.clean(email)

    def get_id(self):
        try:
            id = self.m['Message-Id']
            lhs, host = id[1:-1].split('@')
            date = time.strftime('%Y-%m-%d', self.date)
            return id, 'tag:%s,%s:%s' % (host, date, lhs)
        except KeyError:
            return None, None

    def get_tags(self):
        try:
            tags = self.m['X-Mnemosyne-Tags'].split(',')
            return tags, [self.clean(t) for t in tags]
        except KeyError:
            return [], []

    def get_subject(self):
        try:
            subject = self.m['Subject']
        except KeyError:
            subject = 'Entry'
        cleaned = self.clean(subject, 3)
        u = self.uniq(self.date[0:3], cleaned, self.id)
        print subject, cleaned, u
        return subject, u

    def get_year(self):
        return self.date[0], time.strftime('%Y', self.date)

    def get_month(self):
        return self.date[1], time.strftime('%m', self.date)

    def get_day(self):
        return self.date[2], time.strftime('%d', self.date)
