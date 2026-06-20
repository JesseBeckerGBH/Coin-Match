"""
Database migration helper for research engine tables.
Usage: python -m research.db.migrations create|drop
"""
import sys, os
from sqlalchemy import create_engine
from research.db.models import Base

def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    return create_engine(url)

def create_tables():
    Base.metadata.create_all(get_engine())
    print("Research engine tables created")

def drop_tables():
    Base.metadata.drop_all(get_engine())
    print("Research engine tables dropped")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"create": create_tables, "drop": drop_tables}.get(cmd, lambda: print("Usage: create|drop"))()
