# Mnemosyne configuration
# =======================
#
# This file is a Python script. You can set the following variables here:
#
#   * ``entries_dir``: a Maildir containing all the blog entries.
#   * ``layout_dir``: the blog's layout, as a skeleton directory tree.
#   * ``style_dir``: EmPy templates used for filling the layouts.
#   * ``output_dir``: location where we will write the generated pages.
#
# These default to $HOME/Mnemosyne/{entries,layout,style,htdocs} respectively.
#
#   * ``locals``: a dict of default local variables passed to all templates.
#
# This is initially empty; add anything you want to use in all layouts. This
# example uses ``blogname`` and ``base``.
#
#   * ``ignore``: a list of file names in the layout tree to ignore.
#
# This defaults to ('.svn', 'CVS').
#
# You can also define a class ``EntryMixin`` here. Any methods named
# ``_init_ATTRIBUTE`` or ``_prop_ATTRIBUTE`` will be used to provide
# ``e.ATTRIBUTE`` for each entry ``e``, and will be evaluated at
# initialization or on demand, respectively. (``ATTRIBUTE``, of course, can be
# whatever you want).
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

import mnemosyne

locals['blogname'] = 'Example Blog'
locals['base'] = 'http://example.invalid'

class EntryMixin:
    # Pull anything you want out of the message (self.msg, an
    # email.Message.Message object), and use it to provide a new attribute:

    def _init_foobar(self):
        foobar = self.msg['X-Foobar']
        cleaned = mnemosyne.clean(foobar, 3)
        return mnemosyne.cook(foobar, cleaned)

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
