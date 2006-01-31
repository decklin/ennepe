__name__ = "Month View"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Subjects of all entries from a given month."

def make(instance, entries, all, vars):
    formatted = [muse.expand('subject', e=e, **vars) for e in entries]
    pagetitle = 'Month %s - %s' % (instance, vars['blogtitle'])

    return muse.expand('page', layout=__name__, body="\n".join(formatted),
        pagetitle=pagetitle, **vars)
