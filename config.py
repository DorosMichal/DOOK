from statistics import RequestsNumber, RequestsPerSec, Responses, AvgSizeOf2xx

statistics_list = [RequestsNumber, RequestsPerSec, Responses, AvgSizeOf2xx]
format_str = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
strip_str = '[]"' #used to strip matched group, potentially there could be other brackets etc.
