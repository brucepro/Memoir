"""
chathelper.py - utils to help out parsing the chat

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
 
"""
import re

class ChatHelper:
    def __init__(self):
        pass

    @staticmethod  # Unused, dead code?
    def process_string(input_string):
        pattern = r'\[([^\[\]]+)\]'
        commands_in_string = re.findall(pattern, input_string, re.IGNORECASE)
        print("Processing commands:" + str(commands_in_string))
 
    @staticmethod  # Unused, dead code?
    def safer_string(input_string):
        cleaned_string = re.sub(r'[^a-zA-Z0-9\s]+', '', input_string)
        return cleaned_string

    @staticmethod  # Unused, dead code?
    def remove_dtime(input_string):
        pattern = r"\[DTime=.*?\]"
        new_str = re.sub(pattern, "", input_string)
        return new_str

    @staticmethod
    def check_if_narration(input_string):
        # pattern check if it is narration.
        # set input name for narrator.
        if len(input_string) > 0:
            if input_string[0] == "*" and input_string[-1] == "*":
                return True
        return False

