import time

from paste.translogger import TransLogger

from nicfit.console.ansi import Fg


class ColorTransLogger(TransLogger):

    format = ('%(REMOTE_ADDR)s [%(time)s] '
              '"%(REQUEST_METHOD)s %(REQUEST_URI)s %(HTTP_VERSION)s" '
              '%(status)s %(bytes)s "%(HTTP_REFERER)s" "%(HTTP_USER_AGENT)s"')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def write_log(self, environ, method, req_uri, start, status, bytes):
        if bytes is None:
            bytes = '-'
        if time.daylight:
                offset = time.altzone / 60 / 60 * -100
        else:
                offset = time.timezone / 60 / 60 * -100
        if offset >= 0:
                offset = "+%0.4d" % (offset)
        elif offset < 0:
                offset = "%0.4d" % (offset)
        remote_addr = '-'
        if environ.get('HTTP_X_FORWARDED_FOR'):
            remote_addr = environ['HTTP_X_FORWARDED_FOR']
        elif environ.get('REMOTE_ADDR'):
            remote_addr = environ['REMOTE_ADDR']
        stat = status.split(None, 1)[0]
        user = environ.get("webob._parsed_query_vars")[0].get("u")
        user = environ.get('REMOTE_USER') or user or None
        if user:
            remote_addr = "%s@%s" % (user, remote_addr)
        d = {
            'REMOTE_ADDR': remote_addr,
            'REQUEST_METHOD': method,
            'REQUEST_URI': req_uri,
            'HTTP_VERSION': environ.get('SERVER_PROTOCOL'),
            'time': time.strftime('%d/%b/%Y:%H:%M:%S ', start) + offset,
            'status': stat,
            'bytes': bytes,
            'HTTP_REFERER': environ.get('HTTP_REFERER', '-'),
            'HTTP_USER_AGENT': environ.get('HTTP_USER_AGENT', '-'),
            }
        message = self.format % d
        stat = int(stat)
        if stat >= 200 and stat < 300:
            message = Fg.green(message)
        if stat >= 400 and stat < 500:
            message = Fg.yellow(message)
        if stat >= 500:
            message = Fg.red(message)
        self.logger.log(self.logging_level, message)
