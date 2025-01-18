import sys


def main():
    """Main entry point for the script."""
    try:
        from management.commands_management import ManageCommands
    except ImportError as e:
        raise ImportError(
            "Error: commands_management.py not found. "
        )
    ManageCommands(argv=sys.argv).execute()


if __name__ == "__main__":
    main()
