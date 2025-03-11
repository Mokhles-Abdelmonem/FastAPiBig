import sys


def main():
    """Main entry point for the script."""
    try:
        from FastAPIBig.management.commands_management import ManageCommands
    except ImportError as e:
        raise ImportError(
            "Couldn't import bigfastapi. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    ManageCommands(argv=sys.argv).execute()


if __name__ == "__main__":
    main()
