__name__ = "Tag List"
__author__ = "Decklin Foster"
__email__ = "decklin@red-bean.com"
__description__ = "List of all tags."

def make(instance, entries, all, vars):
    tags = {}
    for e in all:
        for t, _t in zip(e.tags, e._tag):
            tags.setdefault(t, _t)

    formatted = ['<p><a href="%s">%s</a></p>' % (_t, t)
        for t, _t in tags.items()]
    sidebar = muse.expand('sidebar', entries=[], all=[], **vars)
    footer = 'Footer'
    pagetitle = vars['blogtitle']

    return muse.expand('page', layout=__name__, body="\n".join(formatted),
        pagetitle=pagetitle, sidebar=sidebar, footer=footer, **vars)
