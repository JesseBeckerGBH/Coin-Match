"""
Database migration helper for research engine tables.

Usage:
    python -m research.db.migrations create   # Create tables
    python -m research.db.migrations drop     # Drop tables (careful!)
"""
import sys
import os
from sqlalchemy import create_engine
from research.db.models import Base


def get_engine():
    """Create database engine from DATABASE_URL env var."""
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    return create_engine(url)


def create_tables():
    """Create all research engine tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✅ Research engine tables created successfully")


def drop_tables():
    """Drop all research engine tables. Use with caution!"""
    engine = get_engine()
    Base.metadata.drop_all(engine)
    print("⚠️  Research engine tables dropped")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m research.db.migrations [create|drop]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "create":
        create_tables()
    elif command == "drop":
        drop_tables()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
