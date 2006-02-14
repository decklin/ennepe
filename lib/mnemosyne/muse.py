import os
import sys
import mailbox
import time
import stat
import shutil
import kid
import StringIO

import entry
import utils

class Muse:
    def __init__(self, config, force):
        self.force = force
        self.where = []

        default_dir = os.path.join(os.environ['HOME'], 'Mnemosyne')
        self.conf = {
            'entry_dir': os.path.join(default_dir, 'entries'),
            'layout_dir': os.path.join(default_dir, 'layout'),
            'style_dir': os.path.join(default_dir, 'style'),
            'output_dir': os.path.join(default_dir, 'htdocs'),
            'ignore': ('.svn', 'CVS'),
            'locals': {},
            }

        try:
            exec file(config) in self.conf
        except Exception, e:
            raise RuntimeError("Error running config: %s" % e)

        for d in ('entry_dir', 'layout_dir', 'style_dir', 'output_dir'):
            if not os.path.exists(self.conf[d]):
                raise RuntimeError("%s %s does not exist" % (d, self.conf[d]))

        try: entry.Entry.__bases__ += (self.conf['EntryMixin'],)
        except KeyError: pass

        self.box = mailbox.Maildir(self.conf['entry_dir'], entry.Entry)
        self.entries = [e for e in self.box]
        self.entries.sort()

    def sing(self, entries=None, spath=None, dpath=None, what=None):
        """From the contents of spath, build output in dpath, based on the
        provided entries. For each entry in spath, will be called recursively
        with a tuple what representing the source and dest file. For any
        source files starting with __attr__ will recur several times based on
        which entries match each value of that attribute. For regularly named
        files, evaluate them as layout scripts if they are executable and
        simply copy them if they are not."""

        if not entries: entries = self.entries
        if not spath: spath = self.conf['layout_dir']
        if not dpath: dpath = self.conf['output_dir']

        def stale(dpath, spath, entries=None):
            """Test if the file named by dpath is nonexistent or older than
            either the file named by spath or any entry in the given list of
            entries. If --force has been turned on, always return True."""

            if self.force or not os.path.exists(dpath):
                return True
            else:
                dmtime = os.path.getmtime(dpath)
                smtimes = [os.path.getmtime(spath)]
                if entries: smtimes += [time.mktime(e.mtime) for e in entries]
                return dmtime < max(smtimes)

        if what:
            source, dest = what
            spath = os.path.join(spath, source)
            dpath = os.path.join(dpath, dest)
            if source not in self.conf['ignore']:
                if os.path.isfile(spath):
                    if os.stat(spath).st_mode & stat.S_IXUSR:
                        if stale(dpath, spath, entries):
                            self.sing_file(entries, spath, dpath)
                    else:
                        if stale(dpath, spath):
                            shutil.copyfile(spath, dpath)
                            print 'Copied %s' % dpath
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
        """Given a source and dest file in the tuple what, where the source
        starts with __attr__, group the provided entries by the values of that
        attribute over all the provided entries. For an entry e and attribute
        attr, e.attr may be an atomic value or a sequence of values. For each
        value so encountered, evaluate the source file given all entries in
        entries that match that value."""

        subst = what[:what.rindex('__')+2]

        inst = {}
        for e in entries:
            mv = getattr(e, subst[2:-2])
            for m in utils.cheapiter(mv):
                inst.setdefault(repr(m), []).append(e)

        for k, entries in inst.iteritems():
            self.where.append(k)
            self.sing(entries, spath, dpath, (what, what.replace(subst, k)))
            self.where.pop()

    def template(self, name, **kwargs):
        """Open a Kid template in the configuration's style directory, and
        initialize it with any given keyword arguments."""

        path = os.path.join(self.conf['style_dir'], '%s.kid' % name)
        module = kid.load_template(path)
        return module.Template(assume_encoding='utf-8', **kwargs)

    def sing_file(self, entries, spath, dpath):
        """Given an source layout and and dest file, exec it with the locals
        from config plus muse (ourself) and entries (the ones we're actually
        looking at)."""

        locals = self.conf['locals'].copy()
        locals['muse'] = self
        locals['entries'] = entries

        oldstdout = sys.stdout
        sys.stdout = StringIO.StringIO()

        try:
            exec file(spath) in globals(), locals
        except Exception, e:
            raise RuntimeError("Error running layout %s: %s" % (spath, e))

        file(dpath, 'w').write(sys.stdout.getvalue())
        sys.stdout = oldstdout

        print 'Wrote %s' % dpath
