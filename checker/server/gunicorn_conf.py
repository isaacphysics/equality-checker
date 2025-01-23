bind = "0.0.0.0:5000"
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s - %(L)ss'
workers = 1
backlog = 30
preload_app = True
