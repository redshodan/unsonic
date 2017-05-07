import sys
import logging

try:
    # Location of setup_logging in older pyramid versions
    from pyramid.scripts.common import setup_logging
except:
    from pyramid.paster import setup_logging

import eyed3.utils.console


log = logging.getLogger("unsonic")


class StdoutFormatter(logging.Formatter):
    DEFAULT_FORMAT = '%(message)s'

    def __init__(self):
        logging.Formatter.__init__(self, self.DEFAULT_FORMAT)


class FileWrapper(object):
    """A wrapper class for file and file-like objects to provide the same API."""

    def __init__(self, real_file, file_like):
        self._real_file = real_file
        self._file_like = file_like

    def write(self, *args, **kwargs):
        return self._file_like.info(*args, **kwargs)

    def flush(self):
        return self._file_like.handlers[0].flush()

    def isatty(self):
        return self._real_file.isatty()


def setupMash():
    stdout_l = logging.getLogger("mishmash.stdout")
    # FIXME figure out where to put this log file for normal runs
    stdout_handler = logging.StdoutHandler(open("/tmp/foo", "w+"))
    stdout_handler.setFormatter(StdoutFormatter())
    stdout_l.addHandler(stdout_handler)
    stdout_l.setLevel(logging.INFO)
    stdout_l.propagate = False

    wrapper = FileWrapper(sys.stdout, stdout_l)
    eyed3.utils.console.setOutput(wrapper, wrapper)


def resetupLogging(config_uri, global_config):
    setup_logging(config_uri, global_config)
