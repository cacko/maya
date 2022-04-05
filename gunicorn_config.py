bind = '0.0.0.0:6665'
backlog = 2048
workers = 5
worker_class = "gevent"
worker_connections = 100
timeout = 30
keepalive = 2
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%({x-forwarded-for}i)s %(l)s %(t)s "%(r)s" \
    %(s)s %(b)s "%(f)s" "%(a)s"'
worker_tmp_dir = '/dev/shm'
no_sendfile = True
capture_output = True
user = 1001
group = 1001
