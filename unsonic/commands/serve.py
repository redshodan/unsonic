import os, sys, time, tempfile

# from pkg_resources import load_entry_point

from mishmash.commands import command


__requires__ = 'pyramid>=1.4.3'


from pyramid.scripts.pserve import PServeCommand


@command.register
class Serve(command.Command):
    NAME = "serve"

    def __init__(self, subparsers=None):
        super().__init__("Run the unsonic web interface using the Pyramid "
                         "pserve script.", subparsers)
        self.parser.add_argument("--reload",
                                 help="Use auto-restart file monitor")


    def _run(self, args=None):
        args = args or self.args

        wait = 3
        while True:
            try:
                with tempfile.NamedTemporaryFile(mode="w", prefix=".cfg_",
                                                 dir=os.getcwd()) as config_file:
                    self.config.write(config_file)
                    config_file.flush()
                    argv = ["unsonic", config_file.name]
                    pserve = PServeCommand(argv)
                    sys.exit(pserve.run())
                break
            except IndentationError as e:
                if args.reload:
                    print("Failed to (re)start unsonic:", e)
                    print("Restarting in %d seconds..." % wait)
                else:
                    raise
            except SyntaxError as e:
                if args.reload:
                    print("Failed to (re)start unsonic:", e)
                    print("Restarting in %d seconds..." % wait)
                else:
                    raise
            except ImportError as e:
                if args.reload:
                    print("Failed to (re)start unsonic:", e)
                    print("Restarting in %d seconds..." % wait)
                else:
                    raise
            time.sleep(wait)
