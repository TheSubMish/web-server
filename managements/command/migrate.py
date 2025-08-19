# managements/command/migrate.py
import subprocess
from datetime import datetime

MIGRATION_LOG = "migration.log"


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


def get_pending_migrations():
    """Check for pending migrations"""
    try:
        # Get current head
        result = subprocess.run(
            ["alembic", "heads"], capture_output=True, text=True, check=True
        )
        head_revision = result.stdout.strip()

        # Get current database revision
        current_rev = get_current_revision()

        if "No revision found" in current_rev:
            return True, "Database not initialized"
        elif head_revision and head_revision not in current_rev:
            return True, f"Pending migration from {current_rev} to {head_revision}"
        else:
            return False, "Database is up to date"

    except Exception as e:
        log_migration_event(f"Error checking pending migrations: {e}", "ERROR")
        return True, "Error checking migrations"


def show_migration_status():
    """Show current migration status"""
    try:
        log_migration_event("=== Migration Status ===")

        current_rev = get_current_revision()
        log_migration_event(f"Current revision: {current_rev}")

        has_pending, status = get_pending_migrations()
        log_migration_event(f"Status: {status}")

        if has_pending:
            log_migration_event("There are pending migrations to apply", "WARNING")
        else:
            log_migration_event("Database is up to date")

        # Show migration history
        try:
            result = subprocess.run(
                ["alembic", "history", "--verbose"],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout:
                log_migration_event("=== Migration History ===")
                print(result.stdout)
        except:
            log_migration_event("Could not retrieve migration history", "WARNING")

    except Exception as e:
        log_migration_event(f"Error showing migration status: {e}", "ERROR")


def apply_migrations(target: str = "head"):
    """Apply migrations to database"""
    try:
        log_migration_event("=== Starting migration application ===")

        # Check current status
        current_rev = get_current_revision()
        log_migration_event(f"Current revision: {current_rev}")

        has_pending, status = get_pending_migrations()
        if not has_pending and target == "head":
            log_migration_event("No pending migrations to apply")
            return True

        log_migration_event(f"Applying migrations to: {target}")

        # Apply migrations
        result = subprocess.run(
            ["alembic", "upgrade", target], capture_output=True, text=True, check=True
        )

        log_migration_event("Migrations applied successfully")

        # Show output
        if result.stdout:
            log_migration_event("Migration output:")
            print(result.stdout)

        # Show new status
        new_rev = get_current_revision()
        log_migration_event(f"New revision: {new_rev}")

        log_migration_event("=== Migration application completed ===")
        return True

    except subprocess.CalledProcessError as e:
        log_migration_event(f"Migration application failed: {e}", "ERROR")
        if e.stderr:
            log_migration_event(f"Error details: {e.stderr}", "ERROR")
        if e.stdout:
            log_migration_event(f"Output: {e.stdout}", "ERROR")
        return False
    except Exception as e:
        log_migration_event(f"Unexpected error during migration: {e}", "ERROR")
        return False


def rollback_migration(steps: int = 1):
    """Rollback migrations by specified steps"""
    try:
        log_migration_event(f"=== Rolling back {steps} migration(s) ===")

        current_rev = get_current_revision()
        log_migration_event(f"Current revision: {current_rev}")

        if "No revision found" in current_rev:
            log_migration_event("No migrations to rollback", "WARNING")
            return False

        # Rollback
        target = f"-{steps}"
        result = subprocess.run(
            ["alembic", "downgrade", target], capture_output=True, text=True, check=True
        )

        log_migration_event(f"Rollback completed")

        if result.stdout:
            print(result.stdout)

        new_rev = get_current_revision()
        log_migration_event(f"New revision after rollback: {new_rev}")

        return True

    except subprocess.CalledProcessError as e:
        log_migration_event(f"Rollback failed: {e}", "ERROR")
        if e.stderr:
            log_migration_event(f"Error details: {e.stderr}", "ERROR")
        return False
    except Exception as e:
        log_migration_event(f"Unexpected error during rollback: {e}", "ERROR")
        return False


def migrate():
    """Main migrate command function"""
    try:
        log_migration_event("=== Starting migrate command ===")

        # Check if there are any arguments for specific migration targets
        # For now, just apply all pending migrations
        if not apply_migrations("head"):
            log_migration_event("Migration failed", "ERROR")
            return False

        log_migration_event("=== migrate command completed successfully ===")
        return True

    except Exception as e:
        log_migration_event(f"migrate command failed: {e}", "ERROR")
        return False
