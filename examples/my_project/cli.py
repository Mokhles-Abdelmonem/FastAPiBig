def main():
    """Main entry point for the script."""
    try:
        from FastAPIBig.cli import cli
    except ImportError as e:
        raise ImportError(
            "Couldn't import bigfastapi. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    cli()


if __name__ == "__main__":
    main()
