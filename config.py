from statistics_classes import RequestsNumber, RequestsPerSec, Responses, AvgSizeOf2xx
statistics_class_list = [RequestsNumber, RequestsPerSec, Responses, AvgSizeOf2xx]
### for now format_str is required to contain date (t) filed, 
format_str = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# log format:
# remote address
# -
# user name
# date of request
# "status line (GET )"
# status
# response length or '-'
# "refer"
# "user agent"
# request time in microseconds
