import os
import time
from docutils.core import publish_string

def magic_attr(obj, rep):
    class magic_attr(type(obj)):
        def __repr__(self):
            return rep
    return magic_attr(obj)

class BaseEntry:
    def __init__(self, m):
        def fixdate(d):
            # For some bizarre reason, getdate doesn't set wday/yday/isdst...
            return time.localtime(time.mktime(d))
        def getstamp(maildirpath):
            stamp, id, host = os.path.split(maildirpath)[1].split('.')
            return int(stamp)

        self.m = m
        self.date = fixdate(self.m.getdate('Date'))
        self.mtime = time.localtime(getstamp(self.m.fp.name))

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

    def get_content(self):
        SIG_DELIM = '-- \n'
        RST_PREAMBLE = '.. role:: html(raw)\n   :format: html\n\n..\n\n'
        DOC_START = '<div class="document">'
        DOC_END = '</div>'

        s = self.m.fp.read()
        try:
            s = s[:s.rindex(SIG_DELIM)]
        except ValueError:
            pass

        html = publish_string(RST_PREAMBLE + s, writer_name='html')
        try:
            start = html.index(DOC_START) + len(DOC_START)
            end = html.rindex(DOC_END)
            html = html[start:end]
        except ValueError:
            pass

        return magic_attr(html, html[100:])

    def get_author(self):
        author = self.m.getaddr('From')[0]
        return magic_attr(author, self.clean(author))

    def get_email(self):
        email = self.m.getaddr('From')[1]
        return magic_attr(email, self.clean(email))

    def get_id(self):
        try:
            id = self.m['Message-Id']
            lhs, host = id[1:-1].split('@')
            date = time.strftime('%Y-%m-%d', self.date)
            return magic_attr(id, 'tag:%s,%s:%s' % (host, date, lhs))
        except KeyError:
            return None

    def get_tags(self):
        try:
            tags = [t.strip() for t in self.m['X-Mnemosyne-Tags'].split(',')]
            return [magic_attr(t, self.clean(t)) for t in tags]
        except KeyError:
            return []

    def get_subject(self):
        try:
            subject = self.m['Subject']
        except KeyError:
            subject = 'Entry'
        cleaned = self.clean(subject, 3)
        u = self.uniq(self.date[0:3], cleaned, self.id)
        return magic_attr(subject, u)

    def get_year(self):
        return magic_attr(self.date[0], time.strftime('%Y', self.date))

    def get_month(self):
        return magic_attr(self.date[1], time.strftime('%m', self.date))

    def get_day(self):
        return magic_attr(self.date[2], time.strftime('%d', self.date))
