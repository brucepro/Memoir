'''
dream.py
'''
import sqlite3
import os

class Dream():

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
	
