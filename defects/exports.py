import csv
from django.db import connection, connections

def export_table_csv(fp, table_name, connection_name=None):

    conn = connection
    if connection_name is not None:
        conn = connections[connection_name]

    writer = csv.writer(fp)

    with conn.cursor() as c:
        c.execute(f"SELECT * FROM {table_name};")
        headers = [col[0] for col in c.description]
        writer.writerow(headers)
        for row in c.fetchall():
            writer.writerow(row)

    return fp
