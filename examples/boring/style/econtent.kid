<?xml version='1.0' encoding='utf-8'?>
<?python
import time
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<div py:def="contents()">
  <div py:for="e in entries">
    <h2><a
      href="${blogroot}/${repr(e.year)}/${repr(e.month)}/${repr(e.day)}/${repr(e.subject)}.xhtml">${e.subject}</a></h2>
    <div py:replace="XML(e.content)" />
    <p>Posted at
      <a href="${blogroot}/${repr(e.year)}/">${repr(e.year)}</a>-<a
        href="${blogroot}/${repr(e.year)}/${repr(e.month)}/">${repr(e.month)}</a>-<a
        href="${blogroot}/${repr(e.year)}/${repr(e.month)}/${repr(e.day)}/">${repr(e.day)}</a>
      ${time.strftime('%H:%M:%S', e.date)} by
      <a href="mailto:${e.email}">${e.author}</a><br />
      Tags:
      <span py:for="i, t in enumerate(e.tags)" py:strip="True">
        <a href="${blogroot}/tag/${repr(t)}" py:content="t" /><span py:if="i
          != (len(e.tags)-1)" py:strip="True">,</span>
      </span>
    </p>
  </div>
</div>
</html>
