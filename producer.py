import psycopg2
import psycopg2.extras
import random
import smtplib
from datetime import datetime

db_info = {
    'database': 'jobqueue',
    'user': 'postgres',
    'password': '09877890',
    'host': '127.0.0.1',
    'port': '5432',
}

conn = psycopg2.connect(**db_info)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def insert_task():
    try:
        sql_check = """
        SELECT job_id
        FROM jobs
        WHERE status = 'available' OR status = 'failed';
        """
        cur.execute(sql_check)
        checks = cur.fetchall()

        for check in checks:
            sql = """
            INSERT INTO queue(job_id) VALUES(%s);
            """
            cur.execute(sql, (check[0],))
            # import pdb
            # pdb.set_trace()
            sql = """
            UPDATE jobs 
            SET status = 'queued',
                start_time = %s
            WHERE job_id =%s;"""
            cur.execute(sql, [str(datetime.now()), check[0],])
            conn.commit()
            print('inserted task: ', check[0])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


insert_task()
cur.close()
conn.close()