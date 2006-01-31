__name__ = "Tag View"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Contents of entries matching a given tag."

def make(self, entries, vars):
    entries = entries[-50:]
    entries.reverse()
    formatted = [self.expand('entry', e=e, **vars) for e in entries]
    pagetitle = 'Tag "%s" - %s' % (self.instances[-1], vars['blogtitle'])

    return self.expand('page', layout=__name__, body="\n".join(formatted),
        pagetitle=pagetitle, **vars)
