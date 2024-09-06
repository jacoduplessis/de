from django.db import connections
from .models import Incident
from django.utils.timezone import now


def _dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def execute_sql_query(sql, using="default", params=None):
    with connections[using].cursor() as cursor:
        cursor.execute(sql, params=params)
        return _dictfetchall(cursor)


def get_monthly_ri_value_per_area(area_id=None, months=36):
    params = [months]
    area_filter = ""
    if area_id is not None:
        area_filter = "AND i.area_id = %s"
        params.append(area_id)

    sql = f"""
       WITH RECURSIVE dates(date) AS (
    SELECT DATE('now', 'start of month', '-' || %s || ' months')
    UNION ALL
    SELECT DATE(DATE, '+1 months')
    FROM dates
    WHERE DATE(DATE, '+1 months') <= DATE('now', 'start of month')
)
SELECT
    strftime("%%Y-%%m", dates.date) AS label,
    COUNT(i.id) AS cnt,
    IFNULL(SUM(CASE WHEN i.anniversary_success THEN i.rand_value_loss ELSE i.rand_value_loss * -1 END), 0) AS rand_value
FROM
    dates
LEFT JOIN
    defects_incident i
    ON strftime('%%Y-%%m', i.time_start) = strftime('%%Y-%%m', dates.date)
{area_filter}
AND i.time_anniversary_reviewed IS NOT NULL
GROUP BY
    dates.date;
    """
    return execute_sql_query(sql, params=params)

def get_weekly_ri_value_per_area(area_id=None, weeks=52):

    params = [weeks]
    area_filter = ""
    if area_id is not None:
        area_filter = "AND i.area_id = %s"
        params.append(area_id)

    sql = f"""
       WITH RECURSIVE dates(date) AS (
        SELECT DATE(julianday('now') - 7 * %s)
        UNION ALL
        SELECT DATE(julianday(DATE) + 7)
        FROM dates
        WHERE DATE < DATE(julianday('now'))
    )
SELECT
    strftime("%%Y-%%W", dates.date) AS label,
    COUNT(i.id) AS cnt,
    IFNULL(SUM(CASE WHEN i.anniversary_success THEN i.rand_value_loss ELSE i.rand_value_loss * -1 END), 0) AS rand_value
FROM
    dates
LEFT JOIN
    defects_incident i
    ON strftime('%%Y-%%W', i.time_start) = strftime('%%Y-%%W', dates.date)
{area_filter}
AND i.time_anniversary_reviewed IS NOT NULL
GROUP BY
    dates.date;
    """
    return execute_sql_query(sql, params=params)

def get_weekly_ri_count_per_section(section_id, weeks=52):

    sql = f"""
    WITH RECURSIVE dates(date) AS (
        SELECT DATE(julianday('now') - 7 * %s)
        UNION ALL
        SELECT DATE(julianday(DATE) + 7)
        FROM dates
        WHERE DATE < DATE(julianday('now'))
    )
    SELECT
        dates.date AS week_start_date,
        COUNT(i.id) AS cnt,
        IFNULL(SUM(i.rand_value_loss), 0) AS rand_value_loss
    FROM
        dates
    LEFT JOIN
        defects_incident i
        ON strftime('%%Y-%%W', i.time_start) = strftime('%%Y-%%W', dates.date)
    WHERE i.section_id = %s
    GROUP BY
        dates.date;
    """
    return execute_sql_query(sql, params=[weeks, section_id])


def get_section_ri_free_days(section_id):

    last_ri = Incident.objects.filter(section_id=section_id).order_by("-time_end").first()
    if not last_ri:
        return 0
    return (now() - last_ri.time_end).days
