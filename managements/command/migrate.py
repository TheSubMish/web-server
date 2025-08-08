import subprocess


def migrate():
    print("Running migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("Migrations completed successfully.")
