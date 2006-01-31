__name__ = "Tag View"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Contents of entries matching a given tag."

def make(instance, entries, all, vars):
    entries = entries[-50:]
    entries.reverse()
    formatted = [muse.expand('entry', e=e, **vars) for e in entries]
    pagetitle = 'Tag "%s" - %s' % (instance, vars['blogtitle'])

    return muse.expand('page', layout=__name__, body="\n".join(formatted),
        pagetitle=pagetitle, **vars)
