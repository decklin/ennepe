__name__ = "Planet Feed"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Feed of all recent entries tagged 'planet'."

def make(self, entries, vars):
    # XXX: if newer than 1 day
    entries = [e for e in entries if 'planet' in e.tags][-10:]
    entries.reverse()
    return self.expand('atom', entries=entries, **vars)
