__version__ = '0.2'
__author__ = 'Decklin Foster'
__email__ = 'decklin@red-bean.com'
__url__ = 'http://www.red-bean.com/~decklin/software/mnemosyne/'

import os
import mailbox
import time
import stat
import em
import shutil
from rsthtml import publish_content

def magic_attr(obj, rep):
    """Return a subclassed version of obj with its repr() overridden to return
    rep."""

    class Magic(type(obj)):
        def __repr__(self): return rep
    return Magic(obj)

def clean(s, maxwords=None):
    """Split the given string into words, lowercase and strip all
    non-alphanumerics from them, and join them with '-'. If maxwords is given,
    limit the returned string to that many words. If the string is None,
    return None."""

    try:
        words = s.strip().lower().split()[:maxwords]
        words = [''.join([c for c in w if c.isalnum()]) for w in words]
        return '-'.join(words)
    except AttributeError:
        return None

namespaces = {}
def uniq(ns, k, tag):
    """For the given key k, which may come from a group of many keys with the
    same value 'foo', return a string like 'foo', 'foo-1', 'foo-2', etc,
    based on the provided namespace ns (must be a valid dict index) and unique
    identifer tag."""

    ns = namespaces.setdefault(ns, {})
    ns.setdefault(k, {})

    def qual(s, n):
        if n == 0: return s
        else: return '%s-%d' % (s, n)

    if tag not in ns[k].keys():
        ns[k][tag] = qual(k, len(ns[k].keys()))

    return ns[k][tag]

class BaseEntry:
    """Base class for an entry, initialized from an rfc822.Message object
    contained in a mailbox.Maildir. Provides date and mtime attributes, and
    some simple get_* and make_* methods for the derived Entry class to
    call."""

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

    # Remember, get_* is lazy, make_* is not

    def get_content(self):
        """Read in the message's body, strip any signature, and format using
        reStructedText."""

        s = self.m.fp.read()
        try: s = s[:s.rindex('-- \n')]
        except ValueError: pass

        return magic_attr(publish_content(s), s[:100])

    def make_subject(self):
        """Provide the contents of the Subject: header and a cleaned, uniq'd
        version of same."""

        try:
            subject = self.m['Subject']
            cleaned = clean(subject, 3)
        except KeyError:
            subject = ''
            cleaned = 'entry'

        u = uniq(self.date[0:3], cleaned, time.mktime(self.date))
        return magic_attr(subject, u)

    def get_id(self):
        """Provide the Message-ID and a globally unique tag: URL based on it,
        for use in feeds."""

        try:
            id = self.m['Message-Id']
            lhs, host = id[1:-1].split('@')
            date = time.strftime('%Y-%m-%d', self.date)
            return magic_attr(id, 'tag:%s,%s:%s' % (host, date, lhs))
        except KeyError:
            return None

    def get_author(self):
        author = self.m.getaddr('From')[0]
        return magic_attr(author, clean(author))

    def get_email(self):
        """Provide the author's email address and a trivially spam-protected
        version of same."""
        email = self.m.getaddr('From')[1]
        cleaned = email.replace('@', ' at ')
        cleaned = cleaned.replace('.', ' dot ')
        cleaned = cleaned.replace('-', ' dash ')
        return magic_attr(email, cleaned)

    def get_tags(self):
        """Provide a list of tags from the comma-delimited X-Tags: header."""
        try:
            tags = [t.strip() for t in self.m['X-Tags'].split(',')]
            return [magic_attr(t, clean(t)) for t in tags]
        except KeyError:
            return []

    def get_year(self):
        return magic_attr(self.date[0], time.strftime('%Y', self.date))

    def get_month(self):
        return magic_attr(self.date[1], time.strftime('%m', self.date))

    def get_day(self):
        return magic_attr(self.date[2], time.strftime('%d', self.date))

class Muse:
    def __init__(self, config, force):
        DEF_BASE_DIR = os.path.join(os.environ['HOME'], 'Mnemosyne')
        DEF_IGNORE = ('.svn', 'CVS')

        self.where = []
        self.force = force
        self.conf = {
            'entry_dir': os.path.join(DEF_BASE_DIR, 'entries'),
            'layout_dir': os.path.join(DEF_BASE_DIR, 'layout'),
            'style_dir': os.path.join(DEF_BASE_DIR, 'style'),
            'output_dir': os.path.join(DEF_BASE_DIR, 'htdocs'),
            'ignore': DEF_IGNORE,
            'locals': {
                '__version__': __version__,
                '__author__': __author__,
                '__email__': __email__,
                '__url__': __url__,
                },
            }

        if not os.path.exists(config):
            raise RuntimeError("config %s does not exist")

        try:
            exec file(config) in self.conf
        except Exception, e:
            raise RuntimeError("Error running config: %s" % e)

        for d in ('entry_dir', 'layout_dir', 'style_dir', 'output_dir'):
            if not os.path.exists(self.conf[d]):
                raise RuntimeError("%s %s does not exist" % (d, self.conf[d]))

        class NoMixin: pass
        Mixin = self.conf.get('EntryMixin', NoMixin)

        class Entry(Mixin, BaseEntry):
            """Actual entry class. Will search the user-provided mixin class
            and then BaseEntry for methods of the form make_*, and set the
            appropriate attribute on initialization, and also search for
            methods of the form get_* to provide lazily-evaluated attributes
            at runtime."""

            def __getattr__(self, a):
                # get_* is evaluated on demand
                for c in (Mixin, BaseEntry):
                    try:
                        method = getattr(c, 'get_'+a)
                        self.__dict__[a] = method(self)
                        return self.__dict__[a]
                    except AttributeError:
                        pass
                else:
                    return getattr(BaseEntry, a)

        # have to do this after we define Entry but before we iter it
        box = mailbox.Maildir(self.conf['entry_dir'])
        self.entries = [Entry(msg) for msg in box]
        self.entries.sort()

        # make_* is evaluated now
        for c in (Mixin, BaseEntry):
            for n, m in c.__dict__.iteritems():
                if n.startswith('make_'):
                    for e in self.entries:
                        setattr(e, n[5:], m(e))

    def sing(self, entries=None, spath=None, dpath=None, what=None):
        """From the contents of spath, build output in dpath, based on the
        provided entries. For each entry in spath, will be called recursively
        with a tuple what representing the source and dest file. For any
        source files starting with __attr___ will recur several times based on
        which entries match each value of that attribute. For regularly named
        files, evaluate them as layout scripts if they are executable and
        simply copy them if they are not."""

        if not entries: entries = self.entries
        if not spath: spath = self.conf['layout_dir']
        if not dpath: dpath = self.conf['output_dir']

        if what:
            source, dest = what
            spath = os.path.join(spath, source)
            dpath = os.path.join(dpath, dest)
            if source not in self.conf['ignore']:
                if os.path.isfile(spath):
                    if os.stat(spath).st_mode & stat.S_IXUSR:
                        self.sing_file(entries, spath, dpath)
                    else:
                        print 'Copied %s' % dpath
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
        """Given a source and dest file in the tuple what, where the source
        starts with __attr__, group the provided entries by the values of that
        attribute over all the provided entries. For an entry e and attribute
        attr, e.attr may be an atomic value or a sequence of values. For each
        value so encountered, evaluate the source file given all entries in
        entries that match that value."""

        magic = what[:what.rindex('__')+2]
        name = magic[2:-2]

        def cheapiter(x):
            """DWIM-style iterator which, if given a sequence, will iterate
            over that sequence, unless it is a string type. For a string or
            any other atomic type, create an iterator which will return the
            given value once and then stop. This is a horrible kludge."""

            try:
                assert not isinstance((x), (str, unicode))
                for e in x: return iter(x)
                else: return iter(())
            except (AssertionError, TypeError):
                if x: return iter((x,))
                else: return iter(())

        inst = {}
        for e in entries:
            mv = getattr(e, name, None)
            for m in cheapiter(mv):
                inst.setdefault(repr(m), []).append(e)

        for k, entries in inst.iteritems():
            self.where.append(k)
            self.sing(entries, spath, dpath, (what, what.replace(magic, k)))
            self.where.pop()

    def expand(self, style, locals):
        """Open an EmPy file in the configuration's style directory, and
        evaluate it with the given locals."""
        style = os.path.join(self.conf['style_dir'], '%s.empy' % style)
        try:
            return em.expand(file(style).read(), locals)
        except Exception, e:
            raise RuntimeError("Error running style %s: %s" % (style, e))

    def escape(self, s):
        s = s.replace('&', '&amp;')
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')
        return s

    def sing_file(self, entries, spath, dpath):
        """Given an actual source and dest file, where the source is a layout
        script, evaluate it given the locals from config plus muse (ourself),
        write (a callback which actually writes the file), and entries (the
        given entries)."""

        if not self.force and os.path.exists(dpath):
            smtime = max([e.mtime for e in entries])
            dmtime = time.localtime(os.stat(dpath).st_mtime)
            if dmtime > smtime: return

        def write(data):
            file(dpath, 'w').write(data)
            print 'Wrote %s' % dpath

        locals = self.conf['locals'].copy()
        locals['muse'] = self
        locals['write'] = write
        locals['entries'] = entries

        try:
            exec file(spath) in locals
        except Exception, e:
            raise RuntimeError("Error running layout %s: %s" % (spath, e))
