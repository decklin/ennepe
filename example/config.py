# Mnemosyne configuration
# =======================
#
# This file is a Python script. You can set the following variables here:
#
# * ``entries_dir``: a Maildir containing all the blog entries.
# * ``layout_dir``: the blog's layout, as a skeleton directory tree.
# * ``style_dir``: empy styles used for filling layout templates.
# * ``output_dir``: location where we will write the generated pages.
#
# These default to $HOME/Mnemosyne/{entries,layout,style,htdocs} respectively.
#
# * ``locals``: a dict of default local variables passed to all templates.
#
# This initially contains the keys __version__, __url__, __author__, and
# __email__ from Mnemosyne itself. You can of course add other keys for *your*
# name, email, etc, and any other information you want to use in your
# templates.
#
# You can also define a class ``EntryMixin`` here. Any methods named
# ``get_ATTRIBUTE`` will be used to provide ``e.ATTRIBUTE`` for each entry
# ``e``. (``ATTRIBUTE``, of course, can be whatever you want).
#
# The convention used in the default templates is that the repr() of each
# attribute is used to create its URL. For example, if you had a tag called
# 'My Tag', you would return that value, but add a ``__repr__`` method that
# returned 'my-tag', so that you could use it in a link such as
# ``<a href="http://blog/tag/my-tag/">My Tag</a>``. Empy has a nice syntax for
# this, like so: ``<a href="http://blog/tag/@`tag`">@tag</a>``.
#
# To easily create objects that work like this, the ``mnemosyne`` module
# includes a function ``magic_attr`` which takes two arguments: the value
# itself, and the value to use for its repr(). It then takes care of defining
# a new class with a ``__repr__`` method for you.
#
# To easily convert 'My Tag' to 'my-tag', there is also a function ``clean``
# which turns uppercase into lowercase and spaces into dashes, and also allows
# you to limit the number of words included so that URLs do not get too
# unwieldly.

locals['blogname'] = 'Example Blog'
locals['base'] = 'http://example.invalid'

import mnemosyne

class EntryMixin:
    def get_organization(self):
        org = self.m.get('Organization')
        clean = mnemosyne.clean(org, 3)
        return mnemosyne.magic_attr(org, clean)
    #def get_content(self):
    #    s = self.m.fp.read()
    #    return magic_attr(pymarkdown.Markdown(s), s[:100])
