"""
commandhandler.py - main class that parses the chat and checks for commands to run

Memoir+ a persona extension for Text Gen Web UI.
MIT License

Copyright (c) 2024 brucepro

"""

from .persona.persona import Persona
from .commands.urlhandler import UrlHandler
from .commands.file_load import File_Load

import os
import re
from sqlite3 import connect
import pathlib
import validators

class CommandHandler():
    def __init__(self, db_path, character_name):
        self.db_path = db_path
        self.character_name = character_name
        self.commands = {}
        self.command_output = {}

    def process_command(self, input_string):
        pattern = r'\[([^\[\]]+)\]'
        commands_in_string = re.findall(pattern, input_string, re.IGNORECASE)
        #print("Processing commands:" + str(commands_in_string))
 
        # Create an empty list to store the commands
        commands_list = []
        for cmd in commands_in_string:
            command_processed=False
            if command_processed==False:
                if "=" in cmd:
                    command_processed=True
                    print("Processing = command..." + str(cmd))
                    command_parts = cmd.split('=')
                    
                    # Create a new dictionary object for this command
                    commands_list.append({command_parts[0]: {f"arg{i+1}": arg for i, arg in enumerate(command_parts[1].split(','))}})
            if command_processed==False:
                if ":" in cmd:
                
                    command_processed=True
                    print("Processing : command..." + str(cmd))
                    command_parts1 = cmd.split(',')
                    #take each each one and break it down. 
                    for item in command_parts1:
                        command_parts2 = item.split(':')
                        # Create a new dictionary object for this command
                        if len(command_parts2) > 1:
                            commands_list.append({command_parts2[0].strip(): {f"arg{i+1}": arg.strip() for i, arg in enumerate(command_parts2[1].split(','))}})
                   
        print("COMMANDS:" + str(commands_list))
        if len(commands_list) > 0:
            #make sure all the commands are unique and not being spammed. 
            unique_cmds = []
            for cmd in commands_list:
                if cmd not in unique_cmds:
                    unique_cmds.append(cmd)
                    
            for cmd in unique_cmds:
                #URL related commands
                if isinstance(cmd, dict) and "GET_URL" in cmd:
                    args = cmd["GET_URL"]
                    handler = UrlHandler(self.character_name)
                    url =  str(args.get("arg1"))
                    
                    if args.get("arg2"):
                        mode = str(args.get("arg2")).lower().strip()
                    else:
                        mode = 'output'
                    
                    validation = validators.url(url)
                    if validation:
                        print("URL is valid")
                        content = handler.get_url(url, mode=mode)
                        self.command_output["GET_URL"] = f"GET_URL: {content}"

                    else:
                        print("URL is invalid")
                        self.command_output["GET_URL"] = f"GET_URL: URL is invalid"
                
                #FILE LOAD related commands
                if isinstance(cmd, dict) and "FILE_LOAD" in cmd:
                    args = cmd["FILE_LOAD"]
                    
                    file =  str(args.get("arg1"))
                    file_load_handler = File_Load(self.character_name)
                    validation = validators.url(file)
                    is_url = False
                    if validation:
                        print("File is url")
                        is_url = True
                        content = file_load_handler.read_file(file)
                        self.command_output["FILE_LOAD"] = f"FILE_LOAD: {content}"


                    if is_url == False:
                        if os.path.exists(file):
                            print("Path exist")
                            if os.path.isfile(file):
                                print("Path leads to a file")
                                content = file_load_handler.read_file(file)
                                self.command_output["FILE_LOAD"] = f"FILE_LOAD: {content}"
                            elif os.path.isdir(file):
                                directory = file
                                print("Path leads to a directory. This will skip adding to content due to likelihood of extreme length.")
                                count = 0
                                for filename in os.listdir(directory):
                                    # Fixed: Use os.path.join instead of string concatenation
                                    path = os.path.join(directory, filename)
                                    file_load_handler.read_file(path)
                                    count += 1
                                self.command_output["FILE_LOAD"] = f"FILE_LOAD: Successfully ingested {count} total documents."
                        else:
                            print("File does not exist")
                            self.command_output["FILE_LOAD"] = f"FILE_LOAD: File doesn't exist"

        return "\n".join([f"{k}: {v}" for k, v in self.command_output.items()])