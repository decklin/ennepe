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

from entry import BaseEntry

class Muse:
    DEF_BASE_DIR = os.path.join(os.environ['HOME'], 'Mnemosyne')
    IGNORE = ('.svn', 'CVS')

    def __init__(self, configfile):
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
                instances.setdefault(repr(m), [])
                instances[repr(m)].append(e)

        for k, entries in instances.items():
            self.where.append(k)
            self.sing(entries, spath, dpath, (what, what.replace(magic, k)))
            self.where.pop()

    def sing_file(self, entries, spath, dpath):
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
