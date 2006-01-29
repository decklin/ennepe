__name__ = "Year View"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Calendar of all dates in a given year."

import time

def make(instance, entries, all, vars):
    # we get all the entries for this year in ``entries``, in here we want to
    # build some monthly calendars to pass to the next bit
    cal = {}
    for e in entries:
        m = time.strftime('%m', e.date)
        d = time.strftime('%d', e.date)
        cal.setdefault(m, {})
        cal[m].setdefault(d, 0)
        cal[m][d] += 1

    months = [muse.expand('calendar', m=m, days=d, **vars) for m, d in cal.items()]
    sidebar = muse.expand('sidebar', entries=entries, all=all, **vars)
    footer = 'Footer'
    pagetitle = 'Year %s - %s' % (instance, vars['blogtitle'])

    return muse.expand('page', layout=__name__, body="\n".join(months),
        pagetitle=pagetitle, sidebar=sidebar, footer=footer, **vars)
