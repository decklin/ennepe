__name__ = "Day View"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Chronological list of all entries for a given day."

def make(instance, entries, all, vars):
    formatted = [muse.expand('entry', e=e, **vars) for e in entries]
    sidebar = muse.expand('sidebar', entries=entries, all=all, **vars)
    footer = 'Footer'
    pagetitle = 'Day %s - %s' % (instance, vars['blogtitle'])

    return muse.expand('page', layout=__name__, body="\n".join(formatted),
        pagetitle=pagetitle, sidebar=sidebar, footer=footer, **vars)
