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

import entry

class Muse:
    DEF_BASE_DIR = os.path.join(os.environ['HOME'], 'Mnemosyne')
    IGNORE = ('.svn', 'CVS')

    def __init__(self, configfile):
        self.config = {
            'EntryMixin': object,
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

        class Proxy:
            def __init__(self, obj, r):
                self.object = obj
                self.__repr__ = lambda: r
            def __getattr__(self, a):
                return getattr(self.object, a)
            def __eq__(self, other):
                return self.object == other.object

        UserMixin = self.config['EntryMixin']
        class Entry(entry.BaseEntry, entry.Mixin, UserMixin):
            def __getattr__(self, a):
                for c in (UserMixin, entry.Mixin):
                    try:
                        method = getattr(c, 'get_'+a)
                        val, rep = method(self)
                        if type(val) == list:
                            self.__dict__[a] = [Proxy(v, r)
                                for v, r in zip(val, rep)]
                        else:
                            self.__dict__[a] = Proxy(val, rep)
                        return self.__dict__[a]
                    except AttributeError:
                        pass
                return getattr(entry.BaseEntry, a)

        box = mailbox.Maildir(self.config['entry_dir'])
        self.wisdom = [Entry(msg) for msg in box]
        self.wisdom.sort()

        self.where = []

    def sing(self, knowledge=None, spath=None, dpath=None, what=None):
        if not knowledge: knowledge = self.wisdom
        if not spath: spath = self.config['layout_dir']
        if not dpath: dpath = self.config['output_dir']

        if what:
            source, dest = what
            spath = os.path.join(spath, source)
            dpath = os.path.join(dpath, dest)
            if source not in self.IGNORE:
                if os.path.isfile(spath):
                    if os.stat(spath).st_mode & stat.S_IXUSR:
                        self.sing_file(knowledge, spath, dpath)
                    else:
                        shutil.copyfile(spath, dpath)
                elif os.path.isdir(spath):
                    self.sing(knowledge, spath, dpath)
        else:
            if not os.path.isdir(dpath): os.makedirs(dpath)
            for f in os.listdir(spath):
                if f.startswith('__'):
                    self.sing_instances(knowledge, spath, dpath, f)
                else:
                    self.where.append(f)
                    self.sing(knowledge, spath, dpath, (f, f))
                    self.where.pop()

    def sing_instances(self, knowledge, spath, dpath, what):
        magic = what[:what.rfind('__')+2]

        instances = {}
        for e in knowledge:
            mv = getattr(e, magic[2:-2], [])
            if type(mv) != list: mv = [mv] # XXX: ugh
            for v in mv:
                instances.setdefault(repr(v), [])
                instances[repr(v)].append(e)

        for key, entries in instances.items():
            self.where.append(key)
            self.sing(entries, spath, dpath, (what, what.replace(magic, key)))
            self.where.pop()

    def sing_file(self, knowledge, spath, dpath):
        def expand(style, localz):
            stylefile = os.path.join(self.config['style_dir'],
                '%s.empy' % style)
            return em.expand(file(stylefile).read(), localz)
        def write(data):
            file(dpath, 'w').write(data)
            print 'Wrote %s' % dpath

        localz = self.config['locals'].copy()
        localz['self'] = self
        localz['expand'] = expand
        localz['write'] = write
        localz['entries'] = knowledge

        exec file(spath) in localz
