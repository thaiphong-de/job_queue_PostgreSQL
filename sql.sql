--- FOR TABLE JOBS
CREATE TABLE jobs (
  job_id SERIAL PRIMARY KEY,
  status VARCHAR DEFAULT 'available',
  start_time TIMESTAMP DEFAULT NULL,
  end_time TIMESTAMP DEFAULT NULL,
  email VARCHAR,
  content_message VARCHAR
)

--- FOR TABLE QUEUE
CREATE TABLE queue (
  queue_id SERIAL PRIMARY KEY,
  job_id INTEGER
)

--- FOR LISTEN/NOTIFY TASK
CREATE OR REPLACE FUNCTION notify()
RETURNS trigger AS
$BODY$

BEGIN
PERFORM pg_notify('job_queue', NEW.job_id::text);
RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
ALTER FUNCTION notify()
OWNER TO postgres;

CREATE TRIGGER event_trigger
AFTER INSERT
ON queue
FOR EACH ROW
EXECUTE PROCEDURE notify();

--- INSERT COLUMN
INSERT INTO jobs(email, content_mesage) values ('wind2941999@gmail.com', 'test queue')
