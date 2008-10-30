<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<div py:def="contents()">
<?python
import time
import calendar

months = {}
stub = {}
for e in entries:
    months.setdefault(e.month, {}).setdefault(e.day, []).append(e)
    stub[e.month] = e
keys = months.keys()
keys.sort()
?>
  <div py:strip="True" py:for="m in keys">
    <?python
      monthname = time.strftime('%B', months[m].values()[0][0].date)
      cal = calendar.monthcalendar(entries[0].year, m)
    ?>
    <h3><a href="${blogroot}/${`stub[m].year`}/${`stub[m].month`}/">${time.strftime('%B', stub[m].date)}</a></h3>
    <table class="cal">
      <tr class="week" py:for="week in cal">
        <td class="day" py:for="day in week">
          <p>
            <?python e = months[m].get(day, [None])[0] ?>
            <a py:if="months[m].has_key(day)" href="${blogroot}/${`e.year`}/${`e.month`}/${`e.day`}/">${day}</a>
            <span py:if="not months[m].has_key(day)" py:strip="True">
              <span py:if="day" py:strip="True">${day}</span>
            </span>
          </p>
        </td>
      </tr>
    </table>
  </div>
</div>
</html>
