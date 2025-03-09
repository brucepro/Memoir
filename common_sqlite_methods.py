"""
short_term_memory.py - utils for saving stms

Memoir+ a persona extension for Text Gen Web UI.
MIT License

Copyright (c) 2025 corbin-hayden13
"""


import sqlite3
import os


def create_sqlite_db_if_missing(db_name):
    if not os.path.exists(db_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create ShortTermMemory table
        cursor.execute('''CREATE TABLE "short_term_memory" (
                            "id" INTEGER NOT NULL UNIQUE,
                            "memory_text" TEXT NOT NULL,
                            "DateTime" DATETIME DEFAULT CURRENT_TIMESTAMP,
                            "people" TEXT NOT NULL,
                            "memory_type" TEXT,
                            "initiated_by" TEXT,
                            "roleplay" TEXT,
                            "saved_to_longterm" INTEGER,
                            PRIMARY KEY("id" AUTOINCREMENT)
                        )''')

        conn.commit()
        conn.close()