import sys, logging

import eyed3.utils.console


log = logging.getLogger("unsonic")


### Ripped from stdlib logging to remove the extra newline that it puts on
class StdoutHandler(logging.StreamHandler):
    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            fs = "%s"
            if not logging._unicode: #if no unicode support...
                stream.write(fs % msg)
            else:
                try:
                    if (isinstance(msg, str) and
                        getattr(stream, 'encoding', None)):
                        ufs = fs.decode(stream.encoding)
                        try:
                            stream.write(ufs % msg)
                        except UnicodeEncodeError:
                            #Printing to terminals sometimes fails. For example,
                            #with an encoding of 'cp1251', the above write will
                            #work if written to a stream opened or wrapped by
                            #the codecs module, but fail when writing to a
                            #terminal even when the codepage is set to cp1251.
                            #An extra encoding step seems to be needed.
                            stream.write((ufs % msg).encode(stream.encoding))
                    else:
                        stream.write(fs % msg)
                except UnicodeError:
                    stream.write(fs % msg.encode("UTF-8"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class StdoutFormatter(logging.Formatter):
    DEFAULT_FORMAT = '%(message)s'
    
    def __init__(self):
        logging.Formatter.__init__(self, self.DEFAULT_FORMAT)


class FileWrapper(object):
    """
    A wrapper class for file and file-like objects to provide the same API.
    """
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
    stdout_handler = StdoutHandler(open("/tmp/foo", "w+"))
    stdout_handler.setFormatter(StdoutFormatter())
    stdout_l.addHandler(stdout_handler)
    stdout_l.setLevel(logging.INFO)
    stdout_l.propagate = False

    wrapper = FileWrapper(sys.stdout, stdout_l)
    eyed3.utils.console.setOutput(wrapper, wrapper)
