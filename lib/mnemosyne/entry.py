import os
import time
from docutils.core import publish_string

class Entry:
    DOC_START = '<div class="document">'
    DOC_END = '</div>'
    RST_PREAMBLE = '.. role:: html(raw)\n   :format: html\n\n..\n\n'
    SIG_DELIM = '-- \n'

    def __init__(self, m):
        def fixdate(d):
            # For some bizarre reason, getdate doesn't set wday/yday/isdst...
            return time.localtime(time.mktime(d))
        def makeid(date, msgid):
            k, host = msgid[1:-1].split('@')
            return 'tag:%s,%s:%s' % (host, time.strftime('%Y-%m-%d', date), k)
        def getstamp(maildirpath):
            stamp, id, host = os.path.split(maildirpath)[1].split('.')
            return int(stamp)

        # This violates abstraction by poking at m.fp
        self.content = self.publish_html(m.fp.read())
        self.mtime = time.localtime(getstamp(m.fp.name))
        self.date = fixdate(m.getdate('Date'))
        self.id = makeid(self.date, m.get('Message-Id'))
        self.author, self.email = m.getaddr('From')
        self.subject = m.get('Subject')

        try:
            self.tags = map(str.strip, m.get('X-Mnemosyne-Tags').split(','))
        except AttributeError:
            self.tags = []

    def publish_html(self, s):
        try: s = s[:s.rindex(self.SIG_DELIM)]
        except ValueError: pass
        html = publish_string(self.RST_PREAMBLE + s, writer_name='html')
        start = html.find(self.DOC_START) + len(self.DOC_START)
        end = html.rfind(self.DOC_END)
        return html[start:end]

    def __repr__(self):
        return '<Entry about "%s" dated %s>' % (self.subject,
            time.strftime('%Y-%m-%d %H:%M:%S', self.date))

    def __cmp__(self, other):
        return cmp(time.mktime(self.date), time.mktime(other.date))
