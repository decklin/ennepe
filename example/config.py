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
#
# You may also define functions here to add 'magic' attributes to each entry.
# A function with a name of the form ``make_MAGIC`` (which takes a single
# argument, the entry) will be used to create an attribute ``e._MAGIC`` for
# each entry ``e``. Either a single value or a list of values may be returned.
#
# In your layout, a file or directory name containing ``__MAGIC__`` will then
# be evaluated once for each value ``make_MAGIC`` returns, with the entries
# for which ``make_MAGIC`` returns that value or a list containing it.

vars['blogname'] = 'Example Blog'

class Entry:
    def get_organization(self):
        return self.m.get('Organization')
