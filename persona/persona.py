'''
Persona
'''
from textblob import TextBlob
import sqlite3
import os
import re

class Persona:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_sqlite_db_if_missing()

    def create_sqlite_db_if_missing(self):
        if not os.path.exists(self.db_name):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Create Emotions table
            cursor.execute('''CREATE TABLE "Emotions" (
                                "ID" INTEGER,
                                "Thoughts" TEXT,
                                "Emotions" TEXT,
                                "Feelings" TEXT,
                                "Mood" TEXT,
                                "DateTime" DATETIME DEFAULT CURRENT_TIMESTAMP,
                                PRIMARY KEY("ID" AUTOINCREMENT)
                            )''')

            # Create Goals table
            cursor.execute('''CREATE TABLE "goals" (
                                "id" INTEGER NOT NULL UNIQUE,
                                "title" TEXT NOT NULL,
                                "description" TEXT NOT NULL,
                                "importance_rating" INTEGER,
                                "deadline" NUMERIC,
                                "status" INTEGER,
                                "parent_id" INTEGER,
                                "reason" TEXT NOT NULL,
                                "success_criteria" TEXT NOT NULL,
                                PRIMARY KEY("id" AUTOINCREMENT)
                            )''')

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

       
    def calculate_sentiment_score(self, text):
        """Calculates the sentiment score of a given text using TextBlob."""
        blob = TextBlob(text)
        polarity_score = blob.sentiment.polarity  # Score between -1 (negative) and 1 (positive)
        #print("SENTIMENT:" + str(blob.sentiment))
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
        emotions_dict = {}
        num_rows = len(rows)
        polarity_score = None
        for row in rows:
            memory_text = row
            if polarity_score == None:
                polarity_score = self.calculate_sentiment_score(f"{memory_text}")
            else:
                polarity_score = polarity_score + self.calculate_sentiment_score(f"{memory_text}")
    
        average_polarity_score = polarity_score/num_rows

        return average_polarity_score

    def get_emotions_timeframe(self, start_datetime):
        """Queries the emotion entries in the database for a specified time frame."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Thoughts, Emotions, Feelings, Mood, DateTime
            FROM Emotions
            WHERE DateTime >= ?
            ORDER BY DateTime ASC
        """, (start_datetime,))

        rows = cursor.fetchall()
        conn.close()
        emotions_dict = {}

        for row in rows:
            thoughts, emotions, feelings, mood, datetime = row
            if not thoughts or not emotions or not feelings or not mood: continue  # Skip entries with missing data

            polarity_score = self.calculate_sentiment_score(f"{thoughts} {emotions} {feelings} {mood}")

            if emotions not in emotions_dict:
                emotions_dict[emotions] = {
                    "count": 1,
                    "polarity_sum": polarity_score,
                    "first_entry_datetime": datetime
                }
            else:
                emotions_dict[emotions]['count'] += 1
                emotions_dict[emotions]['polarity_sum'] += polarity_score

        for emotion, data in emotions_dict.items():
            data['average_polarity'] = data['polarity_sum'] / data['count']

        return list(emotions_dict.values())

    def add_emotion_to_db(self, thoughts, emotion, feeling, mood):
        """Adds an entry to the database with the given thought, emotion, feeling, and mood."""
        contains_data = 0
        if thoughts != '[]':
        	contains_data = 1
        else:
        	thoughts = ""
        if emotion != '[]':
        	contains_data = 1
        else:
        	emotion = ""
        if feeling != '[]':
        	contains_data = 1
        else:
        	feeling = ""
        if mood != '[]':
        	contains_data = 1
        else:
        	mood = ""
        if contains_data == 1:			
	        sql = "INSERT INTO Emotions (Thoughts, Emotions, Feelings, Mood) VALUES (?, ?, ?, ?)"
	        values = (thoughts, emotion, feeling, mood)
	        conn = sqlite3.connect(self.db_name)
	        cursor = conn.cursor()
	        cursor.execute(sql, values)
	        conn.commit()
	        conn.close()

    def get_emotions_from_string(self,input_string):
        pattern = r'\[([^\[\]]+)\]'
        emotion_output = []
        output = ""
        commands_in_string = re.findall(pattern, input_string, re.IGNORECASE)
        commands_list = []
        for cmd in commands_in_string:
            if ":" in cmd:
                #print("Processing : command..." + str(cmd))
                command_parts1 = cmd.split(',')
                for item in command_parts1:
                    command_parts2 = item.split(':')
                    if len(command_parts2) > 1:
                        commands_list.append({command_parts2[0].strip(): {f"arg{i+1}": arg.strip() for i, arg in enumerate(command_parts2[1].split(','))}})
        for cmd in commands_list:
            if isinstance(cmd, dict) and "EMOTION" in cmd:
                args = cmd["EMOTION"]
                arg1 = str(args.get("arg1"))
                emotion_output.append({"EMOTION": {"arg1": arg1}})
            if isinstance(cmd, dict) and "FEELINGS" in cmd:
                args = cmd["FEELINGS"]
                arg1 = str(args.get("arg1"))
                emotion_output.append({"FEELINGS": {"arg1": arg1}})
            if isinstance(cmd, dict) and "MOOD" in cmd:
                args = cmd["MOOD"]
                arg1 = str(args.get("arg1"))
                emotion_output.append({"MOOD": {"arg1": arg1}}) 
        emotions, feelings, mood = [], [], []
        for key in emotion_output:
            if isinstance(key, dict) and "EMOTION" in key:
                args = key["EMOTION"]
                arg1 = str(args.get("arg1"))
                if arg1 != []:
                    emotions.append(arg1)
            
            if isinstance(key, dict) and "FEELINGS" in key:
                args = key["FEELINGS"]
                arg1 = str(args.get("arg1"))
                if arg1 != []:
                    feelings.append(arg1)
            
            if isinstance(key, dict) and "MOOD" in key:
                args = key["MOOD"]
                arg1 = str(args.get("arg1"))
                if arg1 != []:
                    mood.append(arg1)
        if len(emotions) > 0:
            output = f"EMOTION: {emotions}"
        if len(feelings) > 0:
            output = output + f"FEELINGS: {feelings}"
        if len(mood) > 0:
            output = output + f"MOOD: {mood}"
                         
        return output



