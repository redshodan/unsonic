import unsonic.commands
from mishmash.__main__ import MishMash
from mishmash.commands.command import Command


def run():
    if "web" in Command._all_commands:
        del Command._all_commands["web"]
    app = MishMash()
    app.run()

if __name__ == "__main__":
    run()
