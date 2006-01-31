__name__ = "Day View"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Chronological list of all entries for a given day."

def make(self, entries, vars):
    formatted = [self.expand('entry', e=e, **vars) for e in entries]
    pagetitle = 'Day %s - %s' % (self.instances[-1], vars['blogtitle'])

    return self.expand('page', layout=__name__, body="\n".join(formatted),
        pagetitle=pagetitle, **vars)
