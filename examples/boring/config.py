# Example Mnemosyne configuration
# ===============================
#
# This file is a Python script. 

import os
import mnemosyne

# File locations
# --------------
#
#   * ``entry_dir``: a Maildir containing all the blog entries.
#   * ``layout_dir``: the blog's layout, as a skeleton directory tree.
#   * ``style_dir``: Kid templates used for filling the layouts.
#   * ``output_dir``: location where we will write the generated pages.
#
# All these directories must exist. They default to:

entry_dir = os.path.expanduser('~/Mnemosyne/entries')
layout_dir = os.path.expanduser('~/Mnemosyne/layout')
style_dir = os.path.expanduser('~/Mnemosyne/style')
output_dir = os.path.expanduser('~/Mnemosyne/htdocs')

# Custom Variables
# ----------------
#
#   * ``locals``: a dict of default local variables passed to all templates.
#
# This is initially empty; add anything you want to use in all layouts. This
# example uses:

locals['blogname'] = 'Boring Example'
locals['blogroot'] = 'http://blog.example.invalid'
locals['authname'] = 'Melete'
locals['authemail'] = 'melete@example.invalid'
locals['authhome'] = 'http://www.example.invalid/~melete/'

# Ignore list
# -----------
#
#   * ``ignore``: a list of file names in the layout tree to ignore.
#
# This defaults to:

ignore = ('.svn', 'CVS', 'MT')

# Creating and redefining attributes
# ----------------------------------
#
# You can define a class ``EntryMixin`` in this file. Any methods named
# ``_init_ATTRIBUTE`` or ``_prop_ATTRIBUTE`` will be used to provide
# ``entry.ATTRIBUTE``, and will be evaluated at startup or on demand,
# respectively. (``ATTRIBUTE``, of course, can be whatever you want).
#
# The convention used in the example layout and styles is that the repr() of
# each attribute is used when putting it in a URL. For example, if you had a
# tag called 'My Tag', you would return that value, but add a ``__repr__``
# method that returned 'my-tag', so that you could use it in a link such as
# ``<a href="http://blog/tag/my-tag/">My Tag</a>``.
#
# To easily create objects that work like this, the ``mnemosyne`` module
# includes a function ``cook`` which takes two arguments: the value itself,
# and the value to use for its repr(). It then takes care of defining a new
# class and overriding its ``__repr__`` method for you. Of course, if you do
# not need to define a special repr(), this is not required.
#
# By default, this is not defined.

class EntryMixin:
    # Pull anything you want out of self.msg (an email.Message.Message
    # object), and use it to provide a new attribute. If there is no usable
    # value, make sure there is some default for the repr() so that we don't
    # accidentally create an invalid URL when we use it.

    def _init_foobar(self):
        try:
            foobar = self.msg['X-Foobar']
            cleaned = mnemosyne.utils.clean(foobar, 3)
        except KeyError:
            foobar = ''
            cleaned = 'nofoo'

        return mnemosyne.utils.cook(foobar, cleaned)

    ## You could use Markdown instead of ReST to write entries; I'll comment
    ## this out since you'd need to install it from http://err.no/pymarkdown/
    ## and ``import pymarkdown``.
    #
    ## The formatting process may take a second, so rather than evaluating it
    ## at startup, we will wait until the result is needed. You can apply
    ## other transformations here, or cache the output of your preprocessor;
    ## see mnemosyne.BaseEntry._prop_content for a more involved example.
    #
    #def _prop_content(self):
    #    s = self.msg.get_payload(decode=True)
    #    return mnemosyne.cook(pymarkdown.Markdown(s), s[:100])
