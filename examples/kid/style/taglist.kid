<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<div py:def="body()">
  <p py:for="t, n in tags.iteritems()">
    <a href="${repr(t)}">${t} (${n})</a>
  </p>
</div>

</html>
