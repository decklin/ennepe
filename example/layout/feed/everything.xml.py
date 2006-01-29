__name__ = "Everything Feed"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Feed of all entries."

def make(instance, entries, all, vars):
    entries = entries[-10:] # XXX: if newer than 1 week
    return muse.expand('atom', entries=entries, **vars)
