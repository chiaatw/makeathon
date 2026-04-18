"""
Database connection utilities for Agnes supplement database.

This module provides utilities to connect to the SQLite database and manage
database sessions. Designed to work with the existing db/db.sqlite file.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session
from typing import Optional

from .models import Base


# Global variables for engine and session factory
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_database_url(db_path: Optional[str] = None) -> str:
    """
    Get the database connection URL.

    Args:
        db_path: Optional custom database path. If None, uses default 'db/db.sqlite'

    Returns:
        SQLAlchemy database URL for SQLite connection

    Raises:
        FileNotFoundError: If the database file doesn't exist
    """
    if db_path is None:
        # Default path relative to project root
        db_path = "db/db.sqlite"

    # Convert to absolute path
    db_file = Path(db_path).resolve()

    if not db_file.exists():
        raise FileNotFoundError(f"Database file not found: {db_file}")

    if not db_file.is_file():
        raise ValueError(f"Database path is not a file: {db_file}")

    # Create SQLite URL
    return f"sqlite:///{db_file}"


def get_engine(db_path: Optional[str] = None, echo: bool = False) -> Engine:
    """
    Get or create a SQLAlchemy engine.

    Args:
        db_path: Optional custom database path
        echo: Whether to echo SQL statements (useful for debugging)

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine

    if _engine is None:
        database_url = get_database_url(db_path)
        _engine = create_engine(
            database_url,
            echo=echo,
            # SQLite-specific configurations
            connect_args={"check_same_thread": False}  # Allow multi-threading
        )

    return _engine


def get_session_factory(db_path: Optional[str] = None, echo: bool = False) -> sessionmaker:
    """
    Get or create a SQLAlchemy session factory.

    Args:
        db_path: Optional custom database path
        echo: Whether to echo SQL statements

    Returns:
        SQLAlchemy sessionmaker factory
    """
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine(db_path, echo)
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )

    return _SessionLocal


def get_database_session(db_path: Optional[str] = None, echo: bool = False) -> Session:
    """
    Create a new database session.

    Args:
        db_path: Optional custom database path
        echo: Whether to echo SQL statements

    Returns:
        SQLAlchemy Session instance

    Usage:
        session = get_database_session()
        try:
            # Use session for queries
            companies = session.query(Company).all()
        finally:
            session.close()
    """
    SessionLocal = get_session_factory(db_path, echo)
    return SessionLocal()


def verify_database_schema() -> bool:
    """
    Verify that the database schema matches our model expectations.

    Returns:
        True if schema is valid, False otherwise

    Raises:
        Exception: If there are critical schema mismatches
    """
    try:
        session = get_database_session()

        # Test basic table existence and structure by attempting simple queries
        from .models import Company, Product, BOM, BOMComponent, Supplier, SupplierProduct

        # Test each table with a simple count query
        tables = [
            (Company, "Company"),
            (Product, "Product"),
            (BOM, "BOM"),
            (BOMComponent, "BOM_Component"),
            (Supplier, "Supplier"),
            (SupplierProduct, "Supplier_Product")
        ]

        for model_class, table_name in tables:
            count = session.query(model_class).count()
            if count < 0:  # This should never happen, but let's be safe
                raise ValueError(f"Invalid count for {table_name}: {count}")

        session.close()
        return True

    except Exception as e:
        print(f"Database schema verification failed: {e}")
        return False


def close_connections():
    """
    Close all database connections and reset global state.

    Useful for cleanup in tests or when switching databases.
    """
    global _engine, _SessionLocal

    if _engine is not None:
        _engine.dispose()
        _engine = None

    if _SessionLocal is not None:
        _SessionLocal = None


# Context manager for database sessions
class DatabaseSession:
    """
    Context manager for database sessions with automatic cleanup.

    Usage:
        with DatabaseSession() as session:
            companies = session.query(Company).all()
            # Session is automatically closed
    """

    def __init__(self, db_path: Optional[str] = None, echo: bool = False):
        self.db_path = db_path
        self.echo = echo
        self.session: Optional[Session] = None

    def __enter__(self) -> Session:
        self.session = get_database_session(self.db_path, self.echo)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is not None:
                # Roll back transaction on exception
                self.session.rollback()
            self.session.close()
        return False  # Don't suppress exceptions