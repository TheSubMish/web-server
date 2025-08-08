import os
import subprocess
import configparser
from server.db.database import database


ALEMBIC_DIR = os.path.join(os.getcwd(), "alembic")
ALEMBIC_INI = os.path.join(os.getcwd(), "alembic.ini")


def alembic_initialized():
    return os.path.isdir(ALEMBIC_DIR) and os.path.isfile(ALEMBIC_INI)


def init_alembic():
    database_url = f"sqlite:///{database.db_file}"
    print("Initializing Alembic...")
    subprocess.run(["alembic", "init", "alembic"], check=True)

    # Update alembic.ini with correct database url
    config = configparser.ConfigParser()
    config.read(ALEMBIC_INI)
    if "alembic" not in config:
        config.add_section("alembic")
    config.set("alembic", "sqlalchemy.url", database_url)
    with open(ALEMBIC_INI, "w") as configfile:
        config.write(configfile)

    # Overwrite alembic/env.py with minimal content that imports Base and sets target_metadata
    env_py_content = f"""\
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from server.db.database import Base
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""

    env_py_path = os.path.join(ALEMBIC_DIR, "env.py")
    with open(env_py_path, "w") as f:
        f.write(env_py_content)

    print(f"Alembic initialized and env.py configured with Base.metadata and DB url {database_url}")


def make_migration():
    print("Making migration...")
    subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", "auto migration"], check=True
    )


def makemigrations():
    if not alembic_initialized():
        init_alembic()
    make_migration()
    print("Migration made successfully.")
