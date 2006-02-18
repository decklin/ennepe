<?xml version="1.0" encoding="utf-8"?>
<?python
import time
import datetime
import mnemosyne

def rfc3339(date):
    date = datetime.datetime.fromtimestamp(time.mktime(date))
    return date.isoformat() + 'Z'
?>
<?xml-stylesheet href="http://www.atomenabled.org/css/atom.css" type="text/css"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:py="http://purl.org/kid/ns#">
  <title py:content="blogname" />
  <id>${base}/</id>
  <link rel="self" type="application/atom+xml" href="${'/'.join([base]+muse.where)}" />
  <link rel="alternate" type="application/xhtml+xml" href="${base}/" />
  <updated>${rfc3339(muse.entries[-1].date)}</updated>
  <generator uri="${mnemosyne.__url__}" version="${mnemosyne.__version__}">
    Mnemosyne
  </generator>
  <author>
    <name py:content="blogauthor" />
    <email py:content="blogemail" />
    <uri py:content="bloghome" />
  </author>
  <entry py:for="e in entries">
    <title type="text" py:content="e.subject" />
    <link rel="alternate" type="application/xhtml+xml"
      href="${base}/${repr(e.year)}/${repr(e.month)}/${repr(e.day)}/${repr(e.subject)}.xhtml" />
    <id py:content="repr(e.id)" />
    <published py:content="rfc3339(e.date)" />
    <updated py:content="rfc3339(e.mtime)" />
    <content type="xhtml">
      <div xmlns="http://www.w3.org/1999/xhtml" py:content="XML(e.content)" />
    </content>
  </entry>
</feed>
