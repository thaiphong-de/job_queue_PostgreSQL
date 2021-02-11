# Job queue for send mail using Postgres 

Xây dựng hệ thống hàng đợi xử lý công việc bất đồng bộ dùng Postgre (FOR UPDATE SKIP LOCKED, LISTEN/NOTIFY)

Bao gồm 3 file:

File sql chứa các mã lệnh để tạo các bảng và các thành phần liên quan với pgAdmin4.

File consumer.py có nhiệm vụ subscribe vào queue để lắng nghe thay đổi và thực hiện nhiệm vụ.

File producer.py sẽ đảm nhận lấy task từ table jobs insert vào queue.

## Installation

Python 2,3
PostgreSQL 9.5+

library
```bash
pip install psycopg2
pip install pgnotify
```
Cần cấu hình mail smtp để làm server send mail

Khởi tạo các thông tin kết nối cho python và PostgreSQL bao gồm: 
{
    'database': '',
    'user': '',
    'password': '',
    'host': '',
    'port': '',
}
    
## Usage

```sql
CREATE TABLE jobs (
  job_id SERIAL PRIMARY KEY,
  status VARCHAR DEFAULT 'available',
  start_time TIMESTAMP DEFAULT NULL,
  end_time TIMESTAMP DEFAULT NULL,
  email VARCHAR,
  content_message VARCHAR
)
```
Table jobs sẽ lưu lại thông tin của các job, kể cả đã thực hiện xong để có thể sử dụng báo cáo hay xem xét về sau. Ví dụ, nếu end_time - start_time quá lớn chứng tỏ số lượng job được đẩy vào queue đang quá tải so với worker (xem bên dưới).
Đối với hệ thống send mail, các thuộc tính cần phải có như:
    - job_id: khóa chính.
    - status: thể hiện tình trạng của job, mặc định job mới sẽ được insert vào jobs với status = 'available'(sẵn sàng để insert vào queue). Các status khác của job như: queued(đã thêm vào queue), completed(hoàn thành), failed(thất bại).
    - start_time:(default null) thời điểm job được cho vào queue.
    - end_time:(default null) thời điểm job thực thi xong.
    - email: địa chỉ nhận thư.
    - content_message: nội dung thư.

example 
```sql
INSERT INTO jobs(email, content_message) values ('wind2941999@gmail.com', 'test queue')
```

```sql
CREATE TABLE queue (
  queue_id SERIAL PRIMARY KEY,
  job_id INTEGER
)
```
Table queue đóng vai trò như một hàng đợi, sẽ nhận job vào và điều hướng thực thi cho worker. 
    
## Flow task

Đầu tiên cấu hình và khởi tạo table, function, trigger... ở PostgreSQL.
Sau đó run file consumer để follow các thay đổi trên database như cơ chế subscriber của mesage queue.
Tiếp đó run file producer để chọn và insert job vào queue.

Job sẽ được insert từ table jobs vào table queue (chuyển status từ 'available' sang 'queued'), worker lắng nghe thay đổi ở table queue, nhận và thực thi job. Kết thúc thực thi cập nhật lại status jobs ('completed' nếu thành công hoặc 'failed' nếu thất bại) và xóa job khỏi queue. Những job bị 'failed' sẽ được thực thi lại. Hệ thống cứ thế thực thi cho đến khi không còn job nào tồn tại trong queue. Cơ chế SKIP LOCKED sẽ đảm thực thi job chưa có worker nào nhận cũng như không có job nào được nhiều worker thực thi đồng thời.