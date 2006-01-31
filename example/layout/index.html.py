__name__ = "Recent View"
__author__ = "Decklin Foster"
__email__ = "decklin@red-bean.com"
__description__ = "Contents of recent entries."

def make(instance, entries, all, vars):
    entries = entries[-10:]
    entries.reverse()
    formatted = [muse.expand('entry', e=e, **vars) for e in entries]
    pagetitle = vars['blogtitle']

    return muse.expand('page', layout=__name__, body="\n".join(formatted),
        pagetitle=pagetitle, **vars)
