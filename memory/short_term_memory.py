"""
short_term_memory.py - utils for saving stms

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
"""
import sqlite3
from extensions.Memoir.common_sqlite_methods import create_sqlite_db_if_missing

class ShortTermMemory:
    def __init__(self,db_name):
        
        self.db_name = db_name
        self.conn = None
        self.cursor = None

        create_sqlite_db_if_missing(self.db_name)

    def connect(self):
        try:
            self.conn = sqlite3.connect(f'{self.db_name}')
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)

    def disconnect(self):
        try:
            if self.conn is not None and self.cursor is not None:
                self.cursor = None
                self.conn.close()
        except Exception as e:
            print(e)

    def save_memory(self, memory_text, people, memory_type, initiated_by, roleplay):
        try:
            self.connect()
            sql = """INSERT INTO short_term_memory (
                       memory_text,
                       people,
                       memory_type,
                       initiated_by,
                       roleplay,
                       saved_to_longterm
                     )
                     VALUES (?, ?, ?, ?, ?, 0)"""
            values = (memory_text, people, memory_type, initiated_by, roleplay)
            self.cursor.execute(sql, values)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.disconnect()

    def update_mem_saved_to_longterm(self, mem_id):
        try:
            self.connect()
            sql = f"""UPDATE short_term_memory
                      SET saved_to_longterm=1
                      WHERE id={mem_id}"""
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.disconnect()
