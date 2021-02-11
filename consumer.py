import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import random
import smtplib
from datetime import datetime
import select
import time

db_info = {
    'database': 'jobqueue',
    'user': 'postgres',
    'password': '09877890',
    'host': '127.0.0.1',
    'port': '5432',
}

conn = psycopg2.connect(**db_info)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = conn.cursor()
def send_mail(email, content): 
    gmail_user = 'phong2941999@gmail.com'
    gmail_pwd = 'tybrypebizncfaaf'
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + email + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:job queue \n' + content + '\n'
    print (header)
    msg = header + '\n this is test msg for joc queue system \n\n'
    smtpserver.sendmail(gmail_user, email, msg)
    smtpserver.close()

def process_job():
    try:
        cur.execute("LISTEN job_queue;")
        while True:
            if select.select([conn], [], [], 10) == ([], [], []):
                pass
            else:
                conn.poll()
                while conn.notifies:
                    # notify = conn.notifies.pop(0)
                    sql = """
                    DELETE FROM queue 
                    WHERE job_id = (
                        SELECT job_id
                        FROM queue
                        ORDER BY queue_id
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1
                        )
                    RETURNING job_id;
                    """  
                    cur.execute(sql)
                    queue_item = cur.fetchone()

                    sql_info = """SELECT * FROM jobs WHERE job_id =%s FOR UPDATE;"""
                    cur.execute(sql_info, (queue_item[0],))
                    job_data = cur.fetchone()
                    # import pdb
                    # pdb.set_trace()
                    if job_data:
                        try:
                            send_mail(job_data[4], job_data[5])
                            print('job_id ran: ', job_data[0])
                            sql = """
                                UPDATE jobs 
                                SET status = 'completed',
                                    end_time = %s
                                WHERE job_id =%s;"""
                            
                            cur.execute(sql, [str(datetime.now()), queue_item[0],])
                        except Exception as e:
                            sql = """UPDATE jobs SET status = 'failed' WHERE job_id =%s;"""
                            cur.execute(sql, (queue_item[0],))
                            print('job_id ', queue_item[0], 'failed')
                    else:
                        print('no job found, did not get job id: ', queue_item[0])
                    conn.commit()
                    time.sleep(1)

        print('no change')
    except (Exception, psycopg2.DatabaseError) as error:
        print("queue empty")
       
process_job()
cur.close()
conn.close()