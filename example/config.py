# Mnemosyne configuration
# =======================
#
# This file is a Python script. When run, the following variables will be
# defined for you; you may change or add to them as you see fit.
#
# ``entries_dir``: a Maildir containing all the blog entries.
# ``layout_dir``: the blog's layout, as a skeleton directory tree.
# ``style_dir``: empy styles used for filling layout templates.
# ``output_dir``: location where we will write the generated pages.
#
# These will be $HOME/Mnemosyne/{entries,layout,style,htdocs} respectively.
#
# ``vars``: a dict of default local variables passed to all templates.
#
# This will contain the keys __version__, __url__, __author__, and __email__.

vars['blogtitle'] = 'Changed Things'
vars['blogauthor'] = 'Decklin Foster'
vars['blogemail'] = 'decklin@red-bean.com'
vars['base'] = 'file:///home/decklin/Mnemosyne/htdocs'

# You may also define functions here to add 'magic' attributes to each entry.
# A function with a name of the form ``make_MAGIC`` (which takes a single
# argument, the entry) will be used to create an attribute ``e._MAGIC`` for
# each entry ``e``. Either a single value or a list of values may be returned.
#
# In your layout, a file or directory name containing ``__MAGIC__`` will then
# be evaluated once for each value ``make_MAGIC`` returns, with the entries
# for which ``make_MAGIC`` returns that value or a list containing it.

import time

def make_tag(e):
    return [utils.clean(t) for t in e.tags]

def make_slug(e):
    cleaned = utils.clean(e.subject, 3) or 'entry'
    return utils.unique(e, time.strftime('%Y-%m-%d', e.date), cleaned)

def make_year(e):
    return time.strftime('%Y', e.date)

def make_month(e):
    return time.strftime('%m', e.date)

def make_day(e):
    return time.strftime('%d', e.date)
