import inspect
import unsonic
import unsonic.commands         # noqa: F401
from nicfit import Command

import mishmash
import mishmash.__main__


def buildApp():
    if "web" in Command._all_commands:
        del Command._all_commands["web"]
    if mishmash.commands.web.Web.name in Command._all_commands:
        del Command._all_commands[mishmash.commands.web.Web.name]

    # Temp work around while waiting for mishmash release
    argspec = inspect.getargspec(mishmash.__main__.MishMash.__init__)
    if "progname" in argspec.args:
        return mishmash.__main__.MishMash(progname="unsonic")
    else:
        return mishmash.__main__.MishMash()


def run(args=None):
    app = buildApp()
    return app.run(args)


def main(args=None):
    app = buildApp()
    return app.main(args)


if __name__ == "__main__":
    run()
