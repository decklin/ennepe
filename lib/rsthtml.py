from docutils.core import publish_string

def publish_content(s):
    RST_DELIM = '<!-- CUT -->\n'
    RST_TEMPLATE = """\
.. role:: html(raw)
   :format: html

.. CUT

%s

.. CUT
"""

    html = publish_string(RST_TEMPLATE % s, writer_name='html')
    try:
        start = html.index(RST_DELIM) + len(RST_DELIM)
        end = html.rindex(RST_DELIM)
        return html[start:end]
    except ValueError:
        # This will almost certainly cause whatever includes it to be invalid
        # markup, but it's better than nothing I suppose.
        return html
