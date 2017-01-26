import mishmash.commands
import unsonic.commands
from nicfit import Command
from mishmash.__main__ import MishMash


def run():
    if "web" in Command._all_commands:
        del Command._all_commands["web"]
    if mishmash.commands.web.Web.name in Command._all_commands:
        del Command._all_commands[mishmash.commands.web.Web.name]
    app = MishMash()
    app.run()

if __name__ == "__main__":
    run()
