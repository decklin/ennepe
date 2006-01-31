__name__ = "Year View"
__author__ = "Decklin Foster <decklin@red-bean.com>"
__description__ = "Calendar of all dates in a given year."

import time

def make(self, entries, vars):
    # we get all the entries for this year in ``entries``, in here we want to
    # build some monthly calendars to pass to the next bit
    cal = {}
    for e in entries:
        m = time.strftime('%m', e.date)
        d = time.strftime('%d', e.date)
        cal.setdefault(m, {})
        cal[m].setdefault(d, 0)
        cal[m][d] += 1

    months = [self.expand('calendar', y=self.instances[-1], m=month, days=days, **vars)
        for month, days in cal.items()]
    pagetitle = 'Year %s - %s' % (self.instances[-1], vars['blogtitle'])

    return self.expand('page', layout=__name__, body="\n".join(months),
        pagetitle=pagetitle, **vars)
