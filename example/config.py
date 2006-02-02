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
# __email__ from Mnemosyne itself. You can of course add keys for your
# own name, email, etc, and any other information you want to use in
# your templates. The example templates use ``blogname`` and ``base``.
#
# You can also define a class ``EntryMixin`` here. Any methods named
# ``get_ATTRIBUTE`` will be used to provide ``e.ATTRIBUTE`` for each entry
# ``e``. (``ATTRIBUTE``, of course, can be whatever you want).
#
# The convention used in the example templates is that the repr() of each
# attribute is used when putting it in a URL. For example, if you had a tag
# called 'My Tag', you would return that value, but add a ``__repr__`` method
# that returned 'my-tag', so that you could use it in a link such as ``<a
# href="http://blog/tag/my-tag/">My Tag</a>``. Empy has a nice syntax for
# using repr, which is: ``<a href="http://blog/tag/@`tag`/">@tag</a>``.
#
# To easily create objects that work like this, the ``mnemosyne`` module
# includes a function ``magic_attr`` which takes two arguments: the value
# itself, and the value to use for its repr(). It then takes care of defining
# a new class and overriding its ``__repr__`` method for you. Of course, if
# you do not need to define a special repr(), this is not required.

import mnemosyne

locals['blogname'] = 'Example Blog'
locals['base'] = 'http://example.invalid'

class EntryMixin:
    # Pull anything you want out of the message (self.m, an rfc822.Message
    # object), and use it to provide a new attribute

    def get_foobar(self):
        foobar = self.m.get('X-Foobar')
        cleaned = mnemosyne.clean(foobar, 3)
        return mnemosyne.magic_attr(foobar, cleaned)

    ## You could use Markdown instead of ReST to write entries; I'll comment
    ## this out since you need to install it from http://err.no/pymarkdown/
    #
    #def get_content(self):
    #    s = self.m.fp.read()
    #    try: s = s[:s.rindex('-- \n')]
    #    except ValueError: pass
    #    return magic_attr(pymarkdown.Markdown(s), s[:100])
