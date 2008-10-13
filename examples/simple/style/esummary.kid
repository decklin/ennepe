<?xml version='1.0' encoding='utf-8'?>
<?python
import time
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<div py:def="contents()">
  <p py:for="e in entries">
    ${time.strftime('%a %d %b, %H:%M:%S', e.date)}:
    <a href="${blogroot}/${`e.year`}/${`e.month`}/${`e.day`}/${`e.subject`}.xhtml">${e.subject}</a>
  </p>
</div>
</html>
