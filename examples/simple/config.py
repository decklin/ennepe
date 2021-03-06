# Example Ennepe configuration
# ============================
#
# This file is a Python script. The configuration defined here will
# generate a very simple blog, somewhat like PyBlosxom's defaults.

from ennepe import get_conf, cook, clean

# File locations
# --------------
#
#   * ``entry_dir``: a Maildir containing all the blog entries.
#   * ``layout_dir``: the blog's layout, as a skeleton directory tree.
#   * ``style_dir``: Kid templates used for filling the layouts.
#   * ``output_dir``: location where we will write the generated pages.
#
# All these directories must already exist. They default to the following
# subdirectories of ~/.ennepe:

entry_dir = get_conf('entries')
layout_dir = get_conf('layout')
style_dir = get_conf('style')
output_dir = get_conf('htdocs')

# Custom Variables
# ----------------
#
#   * ``locals``: a dict of local variables passed to all templates.
#
# This is initially empty; add anything you want to use in all layouts.
# Our example uses:

locals['blogname'] = 'Example Blog'
locals['blogroot'] = 'http://blog.polutropon.example/'
locals['authname'] = 'Example Author'
locals['authemail'] = 'blog@polutropon.example'
locals['authhome'] = 'http://www.polutropon.example/'

# Ignore list
# -----------
#
#   * ``ignore``: a list of file names in the layout tree to ignore.
#
# This defaults to:

ignore = ('.hg', '_darcs', '.git', 'MT', '.svn', 'CVS')

# Creating and redefining attributes
# ----------------------------------
#
#   * ``mixins``: a list of classes to search for attribute methods.
#
# You can add attributes to the Entry class by defining your own classes
# here. Any methods named ``get_ATTRIBUTE`` will be used to provide
# ``entry.ATTRIBUTE``, and that value will be automatically cached. To
# use one of these example classes, uncomment it and then add its name to
# the list at the end.
#
# We use the repr() of each attribute when putting it in a URL. For
# example, if you wanted to have a tag called 'My Tag', you would add a
# ``__repr__`` method that returned 'my-tag', so that you could use it
# in a link such as ``<a href="http://blog/tag/my-tag/">My Tag</a>``.
#
# To easily create objects that work like this, we import ``cook``,
# which takes two arguments: a object and a value to override its
# repr(). It does this by defining a new singleton class behind the
# scenes.

#class FooMixin:
#    # Pull anything you want out of self.msg (an email.Message.Message
#    # object), and use it to provide a new attribute. If there is no
#    # usable value, make sure there is some default for the repr() so
#    # that we don't accidentally create an invalid URL when we use it.
#
#    def get_foo(self):
#        try:
#            foo = self.msg['X-Foo']
#            return cook(foo, clean(foo, 3))
#        except KeyError:
#            return cook('', 'xxx-foo-missing')

#class MarkdownMixin:
#    # You could use Markdown instead of ReST to write entries; you'll
#    # need to install it from http://err.no/pymarkdown/.
#
#    import pymarkdown
#
#    def get_content(self):
#        s = self.msg.get_body()
#        return cook(pymarkdown.Markdown(s), s[:80])

#class RawMarkupMixin:
#    # If you would occasionally like to paste a chunk of HTML or
#    # XML from elsewhere into a message, you could use a different
#    # formatter depending on the value of an ``X-Format:`` header. This
#    # uses Expat to ensure that the output is valid XHTML; you could
#    # also use Tidy. Contributed by Aigars Mahinovs.
#
#    import xml.dom
#    import xml.parsers.expat
#
#    def get_content(self):
#        """Read in the message's body, strip any signature, and format using
#        reStructedText unless X-Format=='html'."""
#
#        s = self.msg.get_body(decode=True)
#        body = False
#
#        try:
#            if self.msg['X-Format'] == "html":
#                body = s.replace("&nbsp;", " ")
#                body = re.sub(r'&(?!\w{1,10};)',r'&amp;',body)
#                body = xml.dom.minidom.parseString("<div>" + body +
#                    "</div>").toxml()
#        except KeyError:
#            pass
#        except xml.parsers.expat.ExpatError, e:
#            print "W: Parse failed for " + self.msg['Subject'] + " at " + \
#                self.msg['Date'] + " from " + \
#                str(int(time.mktime(time.strptime(self.msg["Date"],
#                    "%a %b %d %H:%M:%S %Y"))))
#            print xml.parsers.expat.ErrorString(e.code), e.lineno, e.offset
#
#        if not body:
#            parts = docutils.core.publish_parts(s, writer_name='html')
#            body = parts['body']
#
#        return body

mixins = []
