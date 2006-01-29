__name__ = "Entry View"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Permalinkable page for a single entry."

def make(instance, entries, all, vars):
    body = muse.expand('entry', e=entries[0], **vars)
    sidebar = muse.expand('sidebar', entries=entries, all=all, **vars)
    pagetitle = '%s - %s' % (entries[0].subject, vars['blogtitle'])

    return muse.expand('page', layout=__name__, body=body,
        pagetitle=pagetitle, sidebar=sidebar, **vars)
