import sys


def main():
    """Run administrative tasks."""
    try:
        from managements.execute import ExecuteCommand
    except ImportError as exc:
        raise ImportError(
            "Couldn't import managements.execute module. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?"
        )

    command = ExecuteCommand(sys.argv)
    command.execute()


if __name__ == "__main__":
    main()
