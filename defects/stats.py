from django.db import connections


def _dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def execute_sql_query(sql, using="default", params=None):
    with connections[using].cursor() as cursor:
        cursor.execute(sql, params=params)
        return _dictfetchall(cursor)


def get_ri_count_per_section(section_id, weeks=52):

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
