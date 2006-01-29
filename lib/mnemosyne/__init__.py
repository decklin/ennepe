__version__ = '0.1'
__author__ = 'Decklin Foster'
__email__ = 'decklin@red-bean.com'
__url__ = 'http://www.red-bean.com/~decklin/software/mnemosyne/'

import os
import mailbox
import email
import time
import em
import shutil
from docutils.core import publish_string
import mnemosyne.utils

class Entry:
    DOC_START = '<div class="document">'
    DOC_END = '</div>'
    RST_PREAMBLE = '.. role:: html(raw)\n   :format: html\n\n..\n\n'
    SIG_DELIM = '-- \n'

    def __init__(self, source):
        self.content = self.publish_html(source.get_payload())
        self.date = self.parse_date(source['Date'])
        self.id = self.make_id(source['Message-Id'])
        self.author, self.email = email.Utils.parseaddr(source['From'])
        self.subject = source.get('Subject', '')
        self.tags = [t.strip() for t in
            source.get('X-Mnemosyne-Tags', '').split(',') if t]

    def parse_date(self, s):
        # For some bizarre reason, parsedate doesn't set wday/yday/isdst...
        return time.localtime(time.mktime(email.Utils.parsedate(s)))

    def make_id(self, id):
        key, host = id[1:-1].split('@')
        return 'tag:%s,%s:%s' % \
            (host, time.strftime('%Y-%m-%d', self.date), key)

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

class Muse:
    DEF_BASE_DIR = os.path.join(os.environ['HOME'], 'Mnemosyne')

    def __init__(self, configfile):
        self.config = {
            'utils': mnemosyne.utils,
            'entry_dir': os.path.join(self.DEF_BASE_DIR, 'entries'),
            'layout_dir': os.path.join(self.DEF_BASE_DIR, 'layout'),
            'style_dir': os.path.join(self.DEF_BASE_DIR, 'style'),
            'output_dir': os.path.join(self.DEF_BASE_DIR, 'htdocs'),
            'vars': {
                '__version__': __version__,
                '__author__': __author__,
                '__email__': __email__,
                '__url__': __url__,
                },
            }

        exec file(configfile) in self.config

        box = mailbox.Maildir(self.config['entry_dir'],
            email.message_from_file)
        self.wisdom = [Entry(msg) for msg in box]
        self.wisdom.sort()

        self.spells = {}
        for k, v in self.config.items():
            if k.startswith('make_'): self.spells[k[5:]] = v

        for e in self.wisdom:
            for name, spell in self.spells.items():
                setattr(e, '_' + name, spell(e))

    def getf(self, dir, path):
        return os.path.join(self.config[dir+'_dir'], path)

    def sing(self, src='', dest=None, what=None, knowledge=None):
        if not dest: dest = src
        if not what: what = dest
        if not knowledge: knowledge = self.wisdom
        srcbase, srcleaf = os.path.split(src)
        destbase, destleaf = os.path.split(dest)
        realsrc = self.getf('layout', src)
        if destleaf.startswith('__'):
            self.sing_instances(src, dest, what, knowledge)
        elif os.path.isfile(realsrc):
            if srcleaf.endswith('.py'):
                self.sing_file(src, dest[:-3], what, knowledge)
            else:
                shutil.copyfile(realsrc, self.getf('output', dest))
        elif os.path.isdir(realsrc):
            for f in os.listdir(realsrc):
                self.sing(os.path.join(src, f), os.path.join(dest, f),
                    what, knowledge)

    def sing_instances(self, src, dest, what, knowledge):
        srcbase, srcleaf = os.path.split(src)
        xxx = srcleaf[:srcleaf.rfind('__')+2]
        magic = xxx[2:-2]

        instances = {}
        for e in knowledge:
            m_vals = getattr(e, '_' + magic, [])
            if type(m_vals) != list: m_vals = [m_vals]
            for v in m_vals:
                if instances.has_key(v):
                    instances[v].append(e)
                else:
                    instances[v] = [e]

        for k, v in instances.items():
            destbase, destleaf = os.path.split(dest)
            dest = os.path.join(destbase, srcleaf.replace(xxx, k))
            self.sing(src, dest, k, v)

    def expand(self, style, **vars):
        stylefile = self.getf('style', '%s.empy' % style)
        return em.expand(file(stylefile).read(), vars)

    def sing_file(self, src, dest, what, knowledge):
        srcfile = self.getf('layout', src)
        destfile = self.getf('output', dest)

        layout = {'muse': self}
        exec file(srcfile) in layout
        renderer = layout['make']

        page = renderer(what, knowledge, self.wisdom, self.config['vars'])
        self.write(destfile, page)

    def write(self, outfile, data):
        outbase, outleaf = os.path.split(outfile)
        if not os.path.isdir(outbase): os.makedirs(outbase)
        file(outfile, 'w').write(data)
        print 'Wrote %s' % outfile
