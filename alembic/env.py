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
    print(f"Registered tables: {list(Base.metadata.tables.keys())}")
except ImportError as e:
    print(f"Error importing Base: {e}")
    target_metadata = None

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
        print(f"Current database revision: {current_rev or 'None (fresh database)'}")
        
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
            print(f"Migration completed. New revision: {new_rev}")

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
