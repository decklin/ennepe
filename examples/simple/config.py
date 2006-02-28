# Example Mnemosyne configuration
# ===============================
#
# This file is a Python script. The configuration defined here will generate a
# very simple blog, somewhat like PyBlosxom's defaults.

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

locals['blogname'] = 'Simple Example'
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
# To easily create objects that work like this, the ``mnemosyne.utils`` module
# includes a function ``cook`` which takes two arguments: the value itself,
# and the value to use for its repr(). It then takes care of defining a new
# class and overriding its ``__repr__`` method for you. Of course, if you do
# not need to define a special repr(), this is not required.
#
# By default, this class is not defined.

class EntryMixin:
    """User-defined mixin class for Entry objects."""

    ## Pull anything you want out of self.msg (an email.Message.Message
    ## object), and use it to provide a new attribute. If there is no usable
    ## value, make sure there is some default for the repr() so that we don't
    ## accidentally create an invalid URL when we use it.
    #
    #def _init_foobar(self):
    #    try:
    #        foobar = self.msg['X-Foobar']
    #        cleaned = mnemosyne.utils.clean(foobar, 3)
    #    except KeyError:
    #        foobar = ''
    #        cleaned = 'nofoo'
    #
    #    return mnemosyne.utils.cook(foobar, cleaned)

    ## You could use Markdown instead of ReST to write entries; you'll need
    ## to install it from http://err.no/pymarkdown/.
    #
    ## The formatting process may take a second, so rather than evaluating it
    ## at startup, we will wait until the result is needed.
    #
    #import pymarkdown
    #
    #def _prop_content(self):
    #    s = self.msg.get_body()
    #    body = mnemosyne.utils.cook(pymarkdown.Markdown(s), s[:100])
    #    return self.cache('content', body)

    ## If you would occasionally like to paste a chunk of HTML or XML from
    ## elsewhere into a message, you could use a different formatter depending
    ## on the value of an ``X-Format:`` header. This uses Expat to ensure that
    ## the output is valid XHTML; you could also use Tidy. Contributed by
    ## Aigars Mahinovs.
    #
    #import xml.dom
    #import xml.parsers.expat
    #
    #def _prop_content(self):
    #    """Read in the message's body, strip any signature, and format using
    #    reStructedText unless X-Format=='html'."""
    #
    #    s = self.msg.get_body(decode=True)
    #    body = False
    #
    #    try:
    #        if self.msg['X-Format'] == "html":
    #            body = s.replace("&nbsp;", " ")
    #            body = re.sub(r'&(?!\w{1,10};)',r'&amp;',body)
    #            body = xml.dom.minidom.parseString("<div>" + body +
    #                "</div>").toxml()
    #    except KeyError:
    #        pass
    #    except xml.parsers.expat.ExpatError, e:
    #        print "W: Parse failed for " + self.msg['Subject'] + " at " + \
    #            self.msg['Date'] + " from " + \
    #            str(int(time.mktime(time.strptime(self.msg["Date"],
    #                "%a %b %d %H:%M:%S %Y"))))
    #        print xml.parsers.expat.ErrorString(e.code), e.lineno, e.offset
    #
    #    if not body:
    #        parts = docutils.core.publish_parts(s, writer_name='html')
    #        body = parts['body']
    #
    #    return self.cache('content', body)
