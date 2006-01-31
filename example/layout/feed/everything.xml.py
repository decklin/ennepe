__name__ = "Everything Feed"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Feed of all entries."

def make(self, entries, vars):
    entries = entries[-10:] # XXX: if newer than 1 week
    entries.reverse()
    return self.expand('atom', entries=entries, **vars)
