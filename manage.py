import sys


def main() -> None:
    """
    Entry point for running administrative tasks.

    This function attempts to import the `ExecuteCommand` class from the `managements.execute` module.
    If the import fails, it raises an ImportError with a helpful message about possible causes.
    Upon successful import, it creates an instance of `ExecuteCommand` with the command-line arguments
    and executes the command.

    Raises:
        ImportError: If the `managements.execute` module cannot be imported.
    """
    try:
        from managements.execute import ExecuteCommand
    except ImportError as exc:
        raise ImportError(
            "Couldn't import managements.execute module. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?"
        )

    command: ExecuteCommand = ExecuteCommand(sys.argv)
    command.execute()


if __name__ == "__main__":
    main()
