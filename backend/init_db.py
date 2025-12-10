"""
Database initialization script
Run this to create all database tables
"""
from app.database import engine, Base
from app.models.database import User, File, OTP

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")
    print("  - users")
    print("  - otps")
    print("  - files")

if __name__ == "__main__":
    init_db()
