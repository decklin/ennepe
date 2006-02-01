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

import utils
from entry import Entry

class Muse:
    DEF_BASE_DIR = os.path.join(os.environ['HOME'], 'Mnemosyne')
    IGNORE = ('.svn', 'CVS')

    def __init__(self, configfile):
        self.config = {
            'utils': utils,
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

        box = mailbox.Maildir(self.config['entry_dir'])
        self.wisdom = [Entry(msg) for msg in box]
        self.wisdom.sort()

        self.spells = {}
        for k, v in self.config.items():
            if k.startswith('make_'): self.spells[k[5:]] = v

        for e in self.wisdom:
            for name, spell in self.spells.items():
                setattr(e, '_' + name, spell(e))

        self.where = []

    def invoke(self):
        self.sing(self.wisdom,
            self.config['layout_dir'], self.config['output_dir'])

    def sing(self, knowledge, spath, dpath, what=None):
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
            m_vals = getattr(e, '_' + magic[2:-2], [])
            if type(m_vals) != list: m_vals = [m_vals]
            for v in m_vals:
                if instances.has_key(v):
                    instances[v].append(e)
                else:
                    instances[v] = [e]

        for k, v in instances.items():
            self.where.append(k)
            self.sing(v, spath, dpath, (magic, k))
            self.where.pop()

    def expand(self, style, **vars):
        stylefile = os.path.join(self.config['style_dir'], '%s.empy' % style)
        vars['self'] = self
        return em.expand(file(stylefile).read(), vars)

    def sing_file(self, knowledge, spath, dpath):
        layout = {'utils': utils}
        exec file(spath) in layout
        renderer = layout['make']
        page = renderer(self, knowledge, self.config['vars'].copy())
        file(dpath, 'w').write(page)
        print 'Wrote %s' % dpath
