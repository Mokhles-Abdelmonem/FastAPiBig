import sys
from FastAPIBig.management.commands_handlers import (
    startapp_handler,
    runserver_handler,
    help_handler,
    show_help,
    create_tables,
)


class ManageCommands:
    def __init__(self, argv: list = None):
        self.argv = argv or []

    def execute(self):
        if len(self.argv) < 2:
            show_help()
            return

        command = self.argv[1]

        handler = {
            "create_tables": create_tables,
            "startapp": startapp_handler,
            "runserver": runserver_handler,
        }.get(command, help_handler)

        handler(self.argv)


def main():
    ManageCommands(sys.argv).execute()


if __name__ == "__main__":
    main()
