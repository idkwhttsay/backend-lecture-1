#!/usr/bin/env python3
import subprocess
import sys


def create_migration(message: str = None):
    """Create a new migration"""
    cmd = ["alembic", "revision", "--autogenerate"]
    if message:
        cmd.extend(["-m", message])
    subprocess.run(cmd)


def run_migrations():
    """Run pending migrations"""
    subprocess.run(["alembic", "upgrade", "head"])


def downgrade_migration(revision: str = "-1"):
    """Downgrade to specific revision"""
    subprocess.run(["alembic", "downgrade", revision])


def show_history():
    """Show migration history"""
    subprocess.run(["alembic", "history"])


def show_current():
    """Show current revision"""
    subprocess.run(["alembic", "current"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate.py create [message]")
        print("  python migrate.py migrate")
        print("  python migrate.py downgrade [revision]")
        print("  python migrate.py history")
        print("  python migrate.py current")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        create_migration(message)
    elif command == "migrate":
        run_migrations()
    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        downgrade_migration(revision)
    elif command == "history":
        show_history()
    elif command == "current":
        show_current()
    else:
        print(f"Unknown command: {command}")