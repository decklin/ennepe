__version__ = '0.1'
__author__ = 'Decklin Foster'
__email__ = 'decklin@red-bean.com'
__url__ = 'http://www.red-bean.com/~decklin/software/mnemosyne/'

import os
import mailbox
import time
import stat
import em
import shutil
from docutils.core import publish_string

def magic_attr(obj, rep):
    class Magic(type(obj)):
        def __repr__(self):
            return rep
    return Magic(obj)

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

class Muse:
    DEF_BASE_DIR = os.path.join(os.environ['HOME'], 'Mnemosyne')
    IGNORE = ('.svn', 'CVS')

    def __init__(self, configfile, force):
        self.force = force

        self.config = {
            'entry_dir': os.path.join(self.DEF_BASE_DIR, 'entries'),
            'layout_dir': os.path.join(self.DEF_BASE_DIR, 'layout'),
            'style_dir': os.path.join(self.DEF_BASE_DIR, 'style'),
            'output_dir': os.path.join(self.DEF_BASE_DIR, 'htdocs'),
            'locals': {
                '__version__': __version__,
                '__author__': __author__,
                '__email__': __email__,
                '__url__': __url__,
                },
            }

        exec file(configfile) in self.config

        mixin = self.config.get('EntryMixin')
        class Entry(BaseEntry):
            def __getattr__(self, a):
                for c in (mixin, BaseEntry):
                    try:
                        method = getattr(c, 'get_'+a)
                        self.__dict__[a] = method(self)
                        return self.__dict__[a]
                    except AttributeError:
                        pass
                else:
                    return getattr(BaseEntry, a)

        box = mailbox.Maildir(self.config['entry_dir'])
        self.entries = [Entry(msg) for msg in box]
        self.entries.sort()

        self.where = []

    def sing(self, entries=None, spath=None, dpath=None, what=None):
        if not entries: entries = self.entries
        if not spath: spath = self.config['layout_dir']
        if not dpath: dpath = self.config['output_dir']

        if what:
            source, dest = what
            spath = os.path.join(spath, source)
            dpath = os.path.join(dpath, dest)
            if source not in self.IGNORE:
                if os.path.isfile(spath):
                    if os.stat(spath).st_mode & stat.S_IXUSR:
                        self.sing_file(entries, spath, dpath)
                    else:
                        shutil.copyfile(spath, dpath)
                elif os.path.isdir(spath):
                    self.sing(entries, spath, dpath)
        else:
            if not os.path.isdir(dpath): os.makedirs(dpath)
            for f in os.listdir(spath):
                if f.startswith('__'):
                    self.sing_instances(entries, spath, dpath, f)
                else:
                    self.where.append(f)
                    self.sing(entries, spath, dpath, (f, f))
                    self.where.pop()

    def sing_instances(self, entries, spath, dpath, what):
        magic = what[:what.rfind('__')+2]

        instances = {}
        for e in entries:
            mv = getattr(e, magic[2:-2], [])
            if type(mv) != list: mv = [mv] # XXX: ugh
            for m in mv:
                instances.setdefault(m, [])
                instances[m].append(e)

        for k, entries in instances.items():
            self.where.append(k)
            self.sing(entries, spath, dpath,
                (what, what.replace(magic, repr(k))))
            self.where.pop()

    def sing_file(self, entries, spath, dpath):
        if not self.force:
            if os.path.exists(dpath):
                dest_mtime = time.localtime(os.stat(dpath).st_mtime)
                e_mtimes = [e.mtime for e in entries]
                e_mtimes.sort()
                if dest_mtime > e_mtimes[-1]:
                    return

        def expand(style, locals):
            stylefile = os.path.join(self.config['style_dir'],
                '%s.empy' % style)
            return em.expand(file(stylefile).read(), locals)
        def write(data):
            file(dpath, 'w').write(data)
            print 'Wrote %s' % dpath

        locals = self.config['locals'].copy()
        locals['self'] = self
        locals['expand'] = expand
        locals['write'] = write
        locals['entries'] = entries

        exec file(spath) in locals