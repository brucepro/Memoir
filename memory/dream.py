"""
dream.py - main class that handles the retrieval of memories for ltm

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
"""
import sqlite3

class Dream:

	def __init__(self, db_file):
		self.db_file = db_file
		self.conn = sqlite3.connect(self.db_file)
		self.cursor = self.conn.cursor()

	def get_short_term_memories_not_indexed(self,limit):
		conn = sqlite3.connect(self.db_file)
		cursor = conn.cursor()
		cursor.execute(f"SELECT * FROM short_term_memory WHERE saved_to_longterm=0 LIMIT {limit}")
		memories = cursor.fetchall()
		conn.close()
		return memories

	# Unused, dead code?
	def long_form_summary(self,limit):
		conn = sqlite3.connect(self.db_file)
		cursor = conn.cursor()
		cursor.execute(f"SELECT * FROM short_term_memory WHERE saved_to_longterm=1 LIMIT {limit}")
		memories = cursor.fetchall()
		conn.close()
		return memories

	# No usages, long_form_summary is undefined, this is dead code
	# def enter_deep_dream(self):
	# 	memories = long_form_summary(100)
	# 	return memories

