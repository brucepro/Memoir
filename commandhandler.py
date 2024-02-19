'''
CommandHandler.py

'''
from extensions.Memoir.goals.goal import Goal
from extensions.Memoir.persona.persona import Persona
from extensions.Memoir.commands.urlhandler import UrlHandler
from extensions.Memoir.commands.file_load import File_Load

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
        emotion_output = {}
        commands_in_string = re.findall(pattern, input_string, re.IGNORECASE)
        #print("Processing commands:" + str(commands_in_string))
 
        # Create an empty list to store the commands
        commands_list = []
        for cmd in commands_in_string:
            command_processed=False
            if command_processed==False:
                if cmd == "LIST_GOALS":
                    # Create a new dictionary object for this command
                    commands_list.append({"LIST_GOALS": {"arg1": "none"}})
                if cmd == "GOALS_HELP":
                    # Create a new dictionary object for this command
                    commands_list.append({"GOALS_HELP": {"arg1": "none"}})
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
        emotion_output = []
        if len(commands_list) > 0:
            for cmd in commands_list:
                #GOAL related commands
                if isinstance(cmd, dict) and "ADD_GOAL" in cmd:
                # Get the value of the key "ADD_GOAL", which should be another dictionary
                    args = cmd["ADD_GOAL"]
                    # Get the arguments from the dictionary
                    title = args.get("arg1")
                    desc = args.get("arg2")
                    if isinstance(args.get("arg3"),int):
                        imp = int(args.get("arg3"))
                    else:
                        imp = 50
                    new_goal = Goal(title, desc, imp)
                    new_goal.add(connect(self.db_path))
                    self.command_output["ADD_GOAL"] = f"Added goal '{title}' with description: {desc}, importance rating: {imp}"

                if isinstance(cmd, dict) and "DELETE_GOAL" in cmd:
                # Get the value of the key "ADD_GOAL", which should be another dictionary
                    args = cmd["DELETE_GOAL"]
                    # Get the arguments from the dictionary
                    title = args.get("arg1")
                    if isinstance(args.get("arg1"),int):
                        goal_id = int(args.get("arg1"))
                        Goal.delete(connect(self.db_path), goal_id)
                        self.command_output["DELETE_GOAL"] = f"Deleted goal ID: {goal_id}"
                    else:
                        print("Goal id wasn't an int")

                if isinstance(cmd, dict) and "UPDATE_GOAL_STATUS" in cmd:
                # Get the value of the key "ADD_GOAL", which should be another dictionary
                    args = cmd["UPDATE_GOAL_STATUS"]
                    goal_id = args.get("arg1")
                    status = args.get("arg2")
                    print("GOAL ID IS=" + str(goal_id))
                    if isinstance(goal_id,int):
                        Goal.update_goal(connect(self.db_path),goal_id,status)
                        self.command_output["UPDATE_GOAL_STATUS"] = f"Updated goal ID: {goal_id}, status to: {status}"
                    else:
                        print("Goal id wasn't an int")

                if isinstance(cmd, dict) and "LIST_GOALS" in cmd:
                # Get the value of the key "ADD_GOAL", which should be another dictionary
                    args = cmd["LIST_GOALS"]
                    all_goals = Goal.list_current_goals_ordered_by_importance(connect(self.db_path))
                    self.command_output["LIST_GOALS"] = f"Listed current goals: {all_goals}"
                 
                
                if isinstance(cmd, dict) and "GOALS_HELP" in cmd:
                # Get the value of the key "ADD_GOAL", which should be another dictionary
                    #there is a bug here I need to fix.
                    args = cmd["GOALS_HELP"]
                    #show goals help. 
                    helptext = '[ADD_GOAL=New Goal,Description for New Goal,Importance Rating] - Adds a new goal with the given title, description, and importance rating (out of 100) to your knowledge base. For example, to create a goal named "Meditation Practice," with a description of "Develop a consistent meditation practice to improve focus and mental clarity" and an importance rating of 50 out of 100, you would enter:[ADD_GOAL=Meditation Practice,Develop a consistent meditation practice to improve focus and mental clarity,50] You can modify these values as needed.[LIST_GOALS] - Retrieves and lists all current goals stored in your knowledge base, showing their IDs, titles, descriptions, importance ratings, statuses, and completion dates (if applicable).[UPDATE_GOAL_STATUS=id,status] - Changes the status of a specific goal with the given ID to the provided new status (either "complete," "in progress," or "not started"). For example, to update the status of Goal 1 ("Learn a new language") from "Incomplete" to "Complete," you would enter:[UPDATE_GOAL_STATUS=#,complete][DELETE_GOAL=id] - Removes the goal with the given ID from your knowledge base. For example, to delete Goal 1 ("Learn a new language"), you would enter:[DELETE_GOAL=#id of goal from list goals]'

                    self.command_output["GOALS_HELP"] = f"Help text for goals system: {helptext}"
               

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
                            print("file exist")
                            content = file_load_handler.read_file(file)
                            self.command_output["FILE_LOAD"] = f"FILE_LOAD: {content}"

                        else:
                            print("File does not exist")
                            self.command_output["FILE_LOAD"] = f"FILE_LOAD: File doesn't exist"


                     
                #Persona class related commands

                if isinstance(cmd, dict) and "THOUGHTS" in cmd:
                    args = cmd["THOUGHTS"]
                    arg1 = str(args.get("arg1"))
                    emotion_output.append({"THOUGHTS": {"arg1": arg1}}) 
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


            #save the emotions to the emotions table. 
            persona = Persona(self.db_path)
            thoughts, emotions, feelings, mood = [], [], [], []
            for key in emotion_output:
                if isinstance(key, dict) and "THOUGHTS" in key:
                    args = key["THOUGHTS"]
                    arg1 = str(args.get("arg1"))
                    thoughts.append(arg1)
                
                if isinstance(key, dict) and "EMOTION" in key:
                    args = key["EMOTION"]
                    arg1 = str(args.get("arg1"))
                    emotions.append(arg1)
                
                if isinstance(key, dict) and "FEELINGS" in key:
                    args = key["FEELINGS"]
                    arg1 = str(args.get("arg1"))
                    feelings.append(arg1)
                
                if isinstance(key, dict) and "MOOD" in key:
                    args = key["MOOD"]
                    arg1 = str(args.get("arg1"))
                    mood.append(arg1)

            output = f"THOUGHTS: {thoughts} EMOTION: {emotions} FEELINGS: {feelings} MOOD: {mood}"
            persona.add_emotion_to_db(str(thoughts), str(emotions), str(feelings), str(mood))
            


        return "\n".join([f"{k}: {v}" for k, v in self.command_output.items()])