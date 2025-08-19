import os
import subprocess
import configparser
from datetime import datetime
from server.db.database import database

ALEMBIC_DIR = os.path.join(os.getcwd(), "alembic")
ALEMBIC_INI = os.path.join(os.getcwd(), "alembic.ini")
MIGRATION_LOG = os.path.join(os.getcwd(), "migration.log")


def log_migration_event(message: str, level: str = "INFO"):
    """Log migration events with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"

    # Print to console
    print(f"[{level}] {message}")

    # Write to log file
    try:
        with open(MIGRATION_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")


def alembic_initialized():
    """Check if Alembic is properly initialized"""
    has_dir = os.path.isdir(ALEMBIC_DIR)
    has_ini = os.path.isfile(ALEMBIC_INI)
    has_env = os.path.isfile(os.path.join(ALEMBIC_DIR, "env.py"))
    has_versions = os.path.isdir(os.path.join(ALEMBIC_DIR, "versions"))

    return all([has_dir, has_ini, has_env, has_versions])


def validate_database_connection():
    """Validate that database connection works"""
    try:
        database_url = f"sqlite:///{database.db_file}"
        from sqlalchemy import create_engine

        engine = create_engine(database_url)

        with engine.connect() as conn:
            from sqlalchemy import text

            conn.execute(text("SELECT 1"))

        log_migration_event(f"Database connection validated: {database_url}")
        return True
    except Exception as e:
        log_migration_event(f"Database connection failed: {e}", "ERROR")
        return False


def clean_database_state():
    """Clean any existing alembic version table that might be corrupted"""
    try:
        from sqlalchemy import create_engine, text

        database_url = f"sqlite:///{database.db_file}"
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
                )
            ).fetchall()

            if result:
                log_migration_event(
                    "Found existing alembic_version table, cleaning it..."
                )
                conn.execute(text("DROP TABLE alembic_version"))
                conn.commit()
                log_migration_event("Cleaned corrupted alembic_version table")

    except Exception as e:
        log_migration_event(f"Error cleaning database state: {e}", "WARNING")


def init_alembic():
    """Initialize Alembic with enhanced configuration"""
    try:
        database_url = f"sqlite:///{database.db_file}"
        log_migration_event("Initializing Alembic...")

        # Validate database connection first
        if not validate_database_connection():
            log_migration_event(
                "Database validation failed. Aborting initialization.", "ERROR"
            )
            return False

        # Clean any corrupted database state
        clean_database_state()

        # Remove existing alembic directory if it exists to start fresh
        if os.path.exists(ALEMBIC_DIR):
            import shutil

            shutil.rmtree(ALEMBIC_DIR)
            log_migration_event("Removed existing Alembic directory for fresh start")

        if os.path.exists(ALEMBIC_INI):
            os.remove(ALEMBIC_INI)
            log_migration_event("Removed existing alembic.ini for fresh start")

        # Initialize Alembic
        try:
            subprocess.run(["alembic", "init", "alembic"], check=True)
            log_migration_event("Alembic directory structure created")
        except subprocess.CalledProcessError as e:
            log_migration_event(f"Alembic init failed: {e}", "ERROR")
            return False

        # Update alembic.ini with enhanced configuration
        config = configparser.ConfigParser()
        config.read(ALEMBIC_INI)

        if "alembic" not in config:
            config.add_section("alembic")

        # Enhanced alembic configuration
        config.set("alembic", "sqlalchemy.url", database_url)
        config.set(
            "alembic",
            "file_template",
            "%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s",
        )
        config.set("alembic", "timezone", "UTC")
        config.set("alembic", "truncate_slug_length", "40")

        # Write updated configuration
        with open(ALEMBIC_INI, "w") as configfile:
            config.write(configfile)

        log_migration_event(f"Updated alembic.ini with database URL: {database_url}")

        # Create enhanced env.py
        env_py_content = f"""\
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

try:
    from server.db.database import Base
    # Import models through the registry to avoid circular imports
    from server.db.models_registry import import_all_models
    
    # Import all models to register them with Base.metadata
    models = import_all_models()
    
    target_metadata = Base.metadata
    print("Successfully imported Base metadata")
    print(f"Registered tables: {{list(Base.metadata.tables.keys())}}")
except ImportError as e:
    print(f"Error importing Base: {{e}}")
    target_metadata = None

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
        compare_type=True,
        compare_server_default=True,
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
        from alembic.runtime.migration import MigrationContext
        migration_ctx = MigrationContext.configure(connection)
        current_rev = migration_ctx.get_current_revision()
        print(f"Current database revision: {{current_rev or 'None (fresh database)'}}")
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            transaction_per_migration=True,
        )

        with context.begin_transaction():
            context.run_migrations()
            
        new_rev = migration_ctx.get_current_revision()
        if current_rev != new_rev:
            print(f"Migration completed. New revision: {{new_rev}}")

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""

        env_py_path = os.path.join(ALEMBIC_DIR, "env.py")
        with open(env_py_path, "w", encoding="utf-8") as f:
            f.write(env_py_content)

        log_migration_event(
            f"Alembic initialized successfully with enhanced configuration"
        )
        return True

    except Exception as e:
        log_migration_event(f"Failed to initialize Alembic: {e}", "ERROR")
        return False


def create_initial_migration():
    """Create the first migration without autogenerate for clean start"""
    try:
        log_migration_event("Creating initial migration...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        migration_message = f"{timestamp}_initial_migration"

        result = subprocess.run(
            ["alembic", "revision", "-m", migration_message],
            capture_output=True,
            text=True,
            check=True,
        )

        log_migration_event(f"Initial migration created: {migration_message}")
        return True

    except subprocess.CalledProcessError as e:
        log_migration_event(f"Initial migration creation failed: {e}", "ERROR")
        return False


def get_current_revision():
    """Get the current database revision"""
    try:
        result = subprocess.run(
            ["alembic", "current"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "No revision found"
    except Exception as e:
        log_migration_event(f"Error getting current revision: {e}", "ERROR")
        return "Error getting revision"


def create_migration(message: str = "auto migration"):
    """Create a new migration"""
    try:
        log_migration_event(f"Creating migration: {message}")

        current_rev = get_current_revision()
        log_migration_event(f"Current revision before migration: {current_rev}")

        # If no revisions exist, create initial migration first
        if "No revision found" in current_rev:
            log_migration_event(
                "No existing revisions found, creating initial migration first..."
            )
            if not create_initial_migration():
                return False

            # Apply the initial migration
            try:
                subprocess.run(["alembic", "upgrade", "head"], check=True)
                log_migration_event("Initial migration applied successfully")
            except subprocess.CalledProcessError as e:
                log_migration_event(f"Failed to apply initial migration: {e}", "ERROR")
                return False

        # Generate migration
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        migration_message = f"{timestamp}_{message.replace(' ', '_')}"

        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", migration_message],
            capture_output=True,
            text=True,
            check=True,
        )

        log_migration_event(f"Migration created successfully")

        # Show generated files
        if result.stdout:
            lines = result.stdout.strip().split("\n")
            for line in lines:
                if "Generating" in line or "writing" in line:
                    log_migration_event(f"Generated: {line}")

        return True

    except subprocess.CalledProcessError as e:
        log_migration_event(f"Migration creation failed: {e}", "ERROR")
        if e.stderr:
            log_migration_event(f"Error details: {e.stderr}", "ERROR")
        return False
    except Exception as e:
        log_migration_event(f"Unexpected error during migration creation: {e}", "ERROR")
        return False


def makemigrations():
    """Main makemigrations command function"""
    try:
        log_migration_event("=== Starting makemigrations ===")

        # Check if Alembic is initialized
        if not alembic_initialized():
            log_migration_event("Alembic not initialized. Initializing...")
            if not init_alembic():
                log_migration_event("Failed to initialize Alembic", "ERROR")
                return False

        # Validate database connection
        if not validate_database_connection():
            log_migration_event("Database connection validation failed", "ERROR")
            return False

        # Create migration
        if not create_migration("auto migration"):
            log_migration_event("Failed to create migration", "ERROR")
            return False

        log_migration_event("=== makemigrations completed successfully ===")
        return True

    except Exception as e:
        log_migration_event(f"makemigrations failed: {e}", "ERROR")
        return False
