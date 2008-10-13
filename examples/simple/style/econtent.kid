<?xml version='1.0' encoding='utf-8'?>
<?python
import time
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<div py:def="contents()">
  <div py:for="e in entries">
    <h2><a
      href="${blogroot}/${`e.year`}/${`e.month`}/${`e.day`}/${`e.subject`}.xhtml">${e.subject}</a></h2>
    <div py:replace="XML(e.content)" />
    <p>Posted at <a href="${blogroot}/${`e.year`}/">${`e.year`}</a>-<a
        href="${blogroot}/${`e.year`}/${`e.month`}/">${`e.month`}</a>-<a
        href="${blogroot}/${`e.year`}/${`e.month`}/${`e.day`}/">${`e.day`}</a>
      ${time.strftime('%H:%M:%S', e.date)} by
      <a href="mailto:${e.email}">${e.author}</a><br />
      Tags: <span py:for="i, t in enumerate(e.tags)" py:strip="True"><span
        py:if="i > 0" py:strip="True">, </span><a
        href="${blogroot}/tag/${`t`}" py:content="t" /></span>
    </p>
  </div>
</div>
</html>
