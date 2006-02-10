__version__ = '0.6'
__author__ = 'Decklin Foster'
__email__ = 'decklin@red-bean.com'
__url__ = 'http://www.red-bean.com/~decklin/software/mnemosyne/'

import os
import locale
import mailbox
import email, email.Message, email.Header
import time
import stat
import shutil
import em
import kid
import docutils.core

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
            'charset': locale.getpreferredencoding(),
            'locals': {
                '__version__': __version__,
                '__author__': __author__,
                '__email__': __email__,
                '__url__': __url__,
                },
            }

        try:
            exec file(config) in self.conf
        except Exception, e:
            raise RuntimeError("Error running config: %s" % e)

        for d in ('entry_dir', 'layout_dir', 'style_dir', 'output_dir'):
            if not os.path.exists(self.conf[d]):
                raise RuntimeError("%s %s does not exist" % (d, self.conf[d]))

        try: Entry.__bases__ += (self.conf['EntryMixin'],)
        except KeyError: pass

        method = lambda _self, obj, rep: magic(obj, rep, self.conf['charset'])
        Entry.magic = method

        self.box = mailbox.Maildir(self.conf['entry_dir'], Entry)
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

        subst = what[:what.rindex('__')+2]

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
            mv = getattr(e, subst[2:-2])
            for m in cheapiter(mv):
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

    def expand(self, style, locals):
        """Open an EmPy file in the configuration's style directory, and
        evaluate it with the given locals."""
        style = os.path.join(self.conf['style_dir'], '%s.empy' % style)
        try:
            return em.expand(file(style).read(), locals)
        except Exception, e:
            raise RuntimeError("Error running style %s: %s" % (style, e))

    def sing_file(self, entries, spath, dpath):
        """Given an actual source and dest file, where the source is a layout
        script, evaluate it given the locals from config plus muse (ourself),
        write (a callback which actually writes the file), and entries (the
        given entries)."""

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

class BaseEntry:
    """Base class for all entries. Initialized with an open file object, so it
    may be passed to maildir.Maildir as a factory class. Parses the file's
    contents as a Message object, setting a date attribute from the parsed
    date and an mtime attribute from the Maildir filename."""

    def __init__(self, fp):
        def fixdate(d):
            # For some bizarre reason, parsedate doesn't set wday/yday/isdst.
            return time.localtime(time.mktime(d))
        def getstamp(mpath):
            # djb says you're not supposed to do this. djb can bite me.
            stamp, id, host = os.path.split(mpath)[1].split('.')
            return int(stamp)

        self.msg = email.message_from_file(fp, Message)
        self.date = fixdate(email.Utils.parsedate(self.msg['Date']))
        self.mtime = time.localtime(getstamp(fp.name))

    def __cmp__(self, other):
        if other:
            return cmp(time.mktime(self.date), time.mktime(other.date))
        else:
            return 1

    def _prop_content(self):
        """Read in the message's body, strip any signature, and format using
        reStructedText."""

        s = self.msg.get_payload(decode=True)
        if not s: return ''

        try: s = s[:s.rindex('-- \n')]
        except ValueError: pass

        parts = docutils.core.publish_parts(s, writer_name='html')
        body = parts['body']

        self.cache('content', body)
        return body

    byday = {}
    def _init_subject(self):
        """Get the contents of the Subject: header and a cleaned, uniq'd
        version of same."""

        try:
            subject = self.msg['Subject']
            cleaned = clean(subject, 3)
        except KeyError:
            subject = ''
            cleaned = 'entry'

        # Grab the namespace for the day of this entry
        day = self.byday.setdefault(self.date[0:3], UniqueDict())

        slug = day.setdefault(hash(self.msg), cleaned)
        return self.magic(subject, slug)

    def _init_id(self):
        """Get the Message-ID and a globally unique tag: URL based on it, for
        use in feeds."""

        try:
            id = self.msg['Message-Id'][1:-1]
            local, host = id.split('@')
            date = time.strftime('%Y-%m-%d', self.date)
            return self.magic(id, 'tag:%s,%s:%s' % (host, date, local))
        except KeyError:
            return ''

    def _init_author(self):
        """Get the real name portion of the From: address."""
        author, addr = email.Utils.parseaddr(self.msg.get('From'))
        return self.magic(author, clean(author))

    def _init_email(self):
        """Get the author's email address and a trivially spam-protected
        version of same."""
        try:
            author, addr = email.Utils.parseaddr(self.msg['From'])
            cleaned = addr.replace('@', ' at ')
            cleaned = cleaned.replace('.', ' dot ')
            cleaned = cleaned.replace('-', ' dash ')
            return self.magic(addr, cleaned)
        except KeyError:
            return ''

    def _init_tags(self):
        """Get a list of tags from the comma-delimited X-Tags: header."""
        try:
            tags = [t.strip() for t in self.msg['X-Tags'].split(',')]
            return [self.magic(t, clean(t)) for t in tags]
        except KeyError:
            return []

    def _init_year(self):
        """Get the year from the Date: header."""
        return self.magic(self.date[0], time.strftime('%Y', self.date))

    def _init_month(self):
        """Get the month from the Date: header."""
        return self.magic(self.date[1], time.strftime('%m', self.date))

    def _init_day(self):
        """Get the day of the month from the Date: header."""
        return self.magic(self.date[2], time.strftime('%d', self.date))

class Entry(BaseEntry):
    """Actual entry class. Will search the user-provided mixin class and then
    BaseEntry for methods of the form _init_*, and set the appropriate
    attribute on initialization, and also search for methods of the form
    _prop_* to provide properties to be evaluated on demand."""

    def __init__(self, fp):
        for _class in self.__class__.__bases__:
            try: _class.__init__(self, fp)
            except AttributeError: pass

            for k, v in _class.__dict__.iteritems():
                if k.startswith('_init_'):
                    setattr(self, k[6:], v(self))

    attrcache = {}
    def __getattr__(self, a):
        cache = self.attrcache.setdefault(hash(self.msg), {})
        try:
            return cache[a]
        except KeyError:
            for _class in self.__class__.__bases__:
                try:
                    method = getattr(_class, '_prop_'+a)
                    return cache.setdefault(a, method(self))
                except AttributeError:
                    pass
        return getattr(BaseEntry, a)

    def cache(self, attr, val):
        cache = self.attrcache.setdefault(hash(self.msg), {})
        cache[attr] = val

class Message(email.Message.Message):
    """Non-broken version of email's Message class. Returns unicode headers
    when necessary and raises KeyError when appropriate."""

    def __getitem__(self, item):
        header = email.Message.Message.__getitem__(self, item)
        if header:
            # worst. interface. ever.
            parts = email.Header.decode_header(header)
            decoded = []
            for p, enc in parts:
                if enc:
                    decoded.append(unicode(p, enc))
                else:
                    decoded.append(p)
            return ' '.join(decoded)
        else:
            raise KeyError

class UniqueDict(dict):
    """A read-only dict which munges its values so that they are unique. If an
    existing key has the value 'foo', attempting to set another key to 'foo'
    will cause it to become 'foo-1', then 'foo-2', etc. These numberings are
    stable as long as each key is assigned to in the same order; attempting to
    set an existing key will cause a ValueError. """

    def __getitem__(self, k):
        k, i = dict.__getitem__(self, k)
        if i: return '%s-%d' % (k, i)
        else: return k

    def __setitem__(self, k, v):
        if k in self: raise ValueError
        n = len([x for x, y in self.iteritems() if y[0] == v])
        dict.__setitem__(self, k, (v, n))

    # Yes, we must. Le sigh.
    def setdefault(self, key, failobj=None):
        if not self.has_key(key): self[key] = failobj
        return self[key]

def magic(obj, rep, enc):
    """Make obj into something suitable for passing to a layout. Returns an
    object exactly like obj, except its repr() is rep and both are encoded if
    they were unicode (layouts must serialize as a str, so giving them unicode
    data is not recommended). If you are not passing something that might be a
    unicode string, and do not care about using its repr() in your layout, you
    are not required to use this function."""

    if type(obj) is unicode: obj = obj.encode(enc)
    if type(rep) is unicode: rep = rep.encode(enc)

    _class = type("Magic", (type(obj),), {'__repr__': lambda self: rep})
    return _class(obj)

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
