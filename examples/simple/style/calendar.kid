<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<div py:def="contents()">
<?python
import time
import calendar

year = entries[0].date[0]
months = {}
for e in entries:
    months.setdefault(e.month, {})
    months[e.month].setdefault(e.day, [])
    months[e.month][e.day].append(e)
?>
  <div py:strip="True" py:for="m, days in months.iteritems()">
    <?python
      monthname = time.strftime('%B', days.values()[0][0].date)
      cal = calendar.monthcalendar(year, m)
    ?>
    <h3 py:content="monthname" />
    <table class="cal">
      <tr class="week" py:for="week in cal">
        <td class="day" py:for="day in week">
          <p>
            <a py:if="days.has_key(day)" href="${blogroot}/${`e.year`}/${`e.month`}/${`e.day`}/">${day}</a>
            <span py:if="not days.has_key(day)" py:strip="True">
              <span py:if="day" py:strip="True">${day}</span>
            </span>
          </p>
        </td>
      </tr>
    </table>
  </div>
</div>
</html>
