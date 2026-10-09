"""
database.py - Database access layer and schema management for ReturnWise.
Uses SQLite for zero-configuration persistent storage.
"""

import os
import sqlite3
from typing import Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "returnwise.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row access by column name and foreign keys enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(force_recreate: bool = False):
    """Initializes the database schema."""
    if force_recreate and os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Suppliers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        contact_email TEXT,
        category TEXT,
        quality_rating REAL DEFAULT 4.5,
        lead_time_days INTEGER DEFAULT 14,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        supplier_id INTEGER NOT NULL,
        retail_price REAL NOT NULL,
        cost_price REAL NOT NULL,
        units_sold INTEGER DEFAULT 500,
        resale_eligible INTEGER DEFAULT 1,
        processing_cost_base REAL DEFAULT 5.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT
    );
    """)

    # 3. Returns Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS returns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        return_code TEXT UNIQUE NOT NULL,
        order_id TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_reason TEXT NOT NULL,
        customer_comment TEXT,
        return_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending Inspection',
        financial_value REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
    );
    """)

    # 4. Inspections Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        return_id INTEGER UNIQUE NOT NULL,
        inspection_date TEXT NOT NULL,
        inspector_name TEXT NOT NULL,
        item_condition TEXT NOT NULL,
        functionality_status TEXT NOT NULL,
        packaging_condition TEXT NOT NULL,
        missing_components TEXT DEFAULT 'None',
        inspection_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (return_id) REFERENCES returns(id) ON DELETE CASCADE
    );
    """)

    # 5. Recovery Recommendations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recovery_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        return_id INTEGER UNIQUE NOT NULL,
        recommended_action TEXT NOT NULL,
        reason TEXT NOT NULL,
        rule_triggered TEXT NOT NULL,
        evidence_summary TEXT NOT NULL,
        estimated_recovery_value REAL NOT NULL,
        estimated_processing_cost REAL NOT NULL,
        estimated_net_recovery REAL NOT NULL,
        confidence_score TEXT DEFAULT 'High',
        confidence_pct INTEGER DEFAULT 85,
        alternative_actions TEXT,
        status TEXT DEFAULT 'Generated',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (return_id) REFERENCES returns(id) ON DELETE CASCADE
    );
    """)

    # 6. Corrective Actions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS corrective_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        related_type TEXT NOT NULL,
        related_id TEXT NOT NULL,
        priority TEXT NOT NULL,
        evidence TEXT NOT NULL,
        estimated_impact TEXT NOT NULL,
        assigned_to TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Indices for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_product ON returns(product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_status ON returns(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_date ON returns(return_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inspections_return ON inspections(return_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_return ON recovery_recommendations(return_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_actions_status ON corrective_actions(status);")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_FILE)
