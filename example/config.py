# Mnemosyne configuration
# =======================
#
# This file is a Python script. When run, the following variables will be
# defined for you; you may change or add to them as you see fit.
#
# * ``entries_dir``: a Maildir containing all the blog entries.
# * ``layout_dir``: the blog's layout, as a skeleton directory tree.
# * ``style_dir``: empy styles used for filling layout templates.
# * ``output_dir``: location where we will write the generated pages.
#
# These will be $HOME/Mnemosyne/{entries,layout,style,htdocs} respectively.
#
# * ``locals``: a dict of default local variables passed to all templates.
#
# This will contain the keys __version__, __url__, __author__, and __email__.
#
# * ``MnemosyneEntry``: a class used to represent each entry passed to the
#   templates.
#
# If you wish to extend this class, you may define a new class ``Entry`` here,
# using ``MnemosyneEntry`` as its base class. Any methods with a name of the
# form ``get_ATTRIBUTE`` will be used to provide e.ATTRIBUTE at runtime.

locals['blogname'] = 'Example Blog'
locals['base'] = 'http://example.invalid'

class Entry:
    def get_organization(self):
        return self.m.get('Organization')
