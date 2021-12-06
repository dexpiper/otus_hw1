import re


LOG_RECORD_RE = re.compile(
    r'^'
    # remote_addr
    r'\S+ '

    # remote_user (note: ends with double space)
    r'\S+\s+'

    # http_x_real_ip
    r'\S+ '

    # time_local [datetime tz] i.e. [29/Jun/2017:10:46:03 +0300]
    r'\[\S+ \S+\] '

    # request "method href proto" i.e. "GET /api/v2/banner/23815685 HTTP/1.1"
    r'"\S+ (?P<href>\S+) \S+" '

    r'\d+ '      # status
    r'\d+ '      # body_bytes_sent
    r'"\S+" '    # http_referer
    r'".*" '     # http_user_agent
    r'"\S+" '    # http_x_forwarded_for
    r'"\S+" '    # http_X_REQUEST_ID
    r'"\S+" '              # http_X_RB_USER
    r'(?P<time>\d+\.\d+)'  # request_time
)
