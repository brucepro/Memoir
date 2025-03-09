"""
persona.py - various utils to help the A.I. have a persona 

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
"""

from textblob import TextBlob
import sqlite3
import os
from extensions.Memoir.common_sqlite_methods import create_sqlite_db_if_missing

class Persona:
    def __init__(self, db_name):
        self.db_name = db_name

        create_sqlite_db_if_missing(db_name)

    @staticmethod
    def calculate_sentiment_score(text):
        """Calculates the sentiment score of a given text using TextBlob."""
        blob = TextBlob(text)
        polarity_score = blob.sentiment.polarity  # Score between -1 (negative) and 1 (positive)
        return polarity_score

  
    def get_stm_polarity_timeframe(self, start_datetime):
        """Queries the emotion entries in the database for a specified time frame."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT memory_text, DateTime
            FROM short_term_memory
            WHERE DateTime >= ?
            ORDER BY DateTime ASC
        """, (start_datetime,))

        rows = cursor.fetchall()
        conn.close()
        num_rows = len(rows)
        polarity_score = None
        for row in rows:
            memory_text = row
            if not polarity_score:
                polarity_score = self.calculate_sentiment_score(f"{memory_text}")
            else:
                polarity_score = polarity_score + self.calculate_sentiment_score(f"{memory_text}")
        if num_rows > 0:
            average_polarity_score = polarity_score/num_rows
        else:
            average_polarity_score = 0

        return average_polarity_score