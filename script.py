"""
script.py - main entrance of the script into the Text Generation Web UI system extensions

Memoir+ a persona extension for Text Gen Web UI. 

"""

import os
import re
import random
import gradio as gr
import torch
import textwrap
from transformers import LogitsProcessor
from datetime import datetime, timedelta 
from modules import chat, shared, utils
from modules.text_generation import (
    decode,
    encode,
    generate_reply,
)
import pathlib
import sqlite3
import subprocess
import itertools
from python_on_whales import DockerClient


from extensions.webui_memoir.goals.goal import Goal
from extensions.webui_memoir.commandhandler import CommandHandler
from extensions.webui_memoir.chathelper import ChatHelper
from extensions.webui_memoir.memory.short_term_memory import ShortTermMemory
from extensions.webui_memoir.memory.long_term_memory import LTM
from extensions.webui_memoir.memory.dream import Dream
from extensions.webui_memoir.persona.persona import Persona

#globals
current_dir = os.path.dirname(os.path.abspath(__file__))
memoir_js = os.path.join(current_dir, "memoir.js")
memoir_css = os.path.join(current_dir, "memoir.css")
databasepath = os.path.join(current_dir, "storage/sqlite/") 
bot_long_term_memories = ""  #saved after output generation and added to the next input.


params = {
    "display_name": "Memoir+",
    "is_tab": False,
    "ltm_limit": 5,
    "ego_summary_limit": 10,
    "is_roleplay": False,
    'memory_active': True,
    "current_selected_character": None,
    "qdrant_address": "http://localhost:6333",
    "query_output": "vdb search results",
    'verbose': False,
    'polarity_score': 0,
    'dream_mode': 0,
    'activate_narrator': False,
    'use_thinking_emotes': True,
    'thinking_emotes': ['Deep in thought...','Pondering deeply...', 'Gathering my thoughts...','Organizing my ideas...', 'Taking it all in...','Absorbing the information provided...', 'Mulling it over...','Reflecting on your request...', 'Delving into the matter...','Diving deep into thought...', 'Thinking hard...','Concentrating intensely...', 'Considering all angles...','Examining every possibility...', 'Evaluating options...','Weighing up your request...', 'Deliberating carefully...','Carefully assessing the situation...', 'Musing over possibilities...','Dreamily pondering various outcomes...', 'Engrossed in thought...','Completely absorbed in my thoughts...', 'Analyzing information...','Dissecting your request into its constituent parts...', 'Formulating a response...','Creating the perfect reply for you...', 'Taking it all into account...','Incorporating every detail of your input...', 'Weighing up factors...','Considering the impact of each aspect of your request...', 'Meditating on a solution...','Seeking a response that will satisfy both you and my principles...', 'Reflecting intently...','Thoughtfully assessing every angle of your prompt...', 'Assessing the situation...','Carefully evaluating your needs...', 'Sifting through ideas...','Examining different approaches to address your query...', 'Piecing together a response...','Composing an answer that will meet your expectations...', 'Delving into the matter...','Diving deep into thought...', 'Taking it all in...','Absorbing the information provided...'],
    'thinking_emotes_negative_polarity': ['Deeply troubled...', 'Tormented by thought...', 'Plagued by doubts...'],
    'thinking_emotes_slightly_negative_polarity': ['Feeling down...', 'Gloomy thoughts...', 'Pessimistic musings...'],
    'thinking_emotes_neutral_polarity': ['Thinking...','Thinking it over...', 'Deliberating carefully...', 'Evaluating options...'],
    'thinking_emotes_slightly_positive_polarity': ['Feeling optimistic...', 'Looking forward to possibilities...', 'Excited about ideas...'],
    'thinking_emotes_positive_polarity': ['Brimming with enthusiasm...', 'Eagerly contemplating the future...', 'Gleefully anticipating opportunities...'],

}


def state_modifier(state):
    """
    Modifies the state variable, which is a dictionary containing the input
    values in the UI like sliders and checkboxes.
    """
    state['ltm_limit'] = params['ltm_limit']
    state['ego_summary_limit'] = params['ego_summary_limit']
    state['polarity_score'] = params['polarity_score']
    state['dream_mode'] = params['dream_mode']
    state['is_roleplay'] = params['is_roleplay']

    state['memory_active'] = params['memory_active']
    state['qdrant_address'] = params['qdrant_address']
    state['polarity_score'] = params['polarity_score']
    state['use_thinking_emotes'] = params['use_thinking_emotes']
    state['current_selected_character'] = params['current_selected_character']
    '''
    Since we are adding to the bot prefix, they tend to get hung up on 
    using the prefix. Good spot to give extra instructions, but we need
    add the stop string. Also when the bot speaks as the user it is annoying,
    so fix for that.
    '''
    state['custom_stopping_strings'] = '"[DTime=","[24hour Average Polarity Score=", "' + str(state["name1"].strip()) +':"'

    if params['verbose'] == True:
        print("----------------State Modifer-------------")
        #print(state)
        print("----------------End State Modifer-------------")
    return state


def bot_prefix_modifier(string, state):
    """
    Modifies the prefix for the next bot reply in chat mode.
    By default, the prefix will be something like "Bot Name:".
    """
    if params['verbose'] == True:
        print("polarity_score:" + str(params['polarity_score']) + "use_thinking_emotes:" + str(params['use_thinking_emotes']))
    if params['use_thinking_emotes'] == True:
        if params['polarity_score'] < -0.699999999999999:
            shared.processing_message = random.choice(list(params['thinking_emotes_negative_polarity']))
        elif params['polarity_score'] >= -0.700000000000000 and params['polarity_score'] < 0:
            shared.processing_message = random.choice(list(params['thinking_emotes_slightly_negative_polarity']))
        elif params['polarity_score'] >= 0 and params['polarity_score'] < 0.48900000000:
            shared.processing_message = random.choice(list(params['thinking_emotes_neutral_polarity']))
        elif params['polarity_score'] >= 0.4999999999999999 and params['polarity_score'] < 0.75:
            shared.processing_message = random.choice(list(params['thinking_emotes_slightly_positive_polarity']))
        elif params['polarity_score'] >= 0.75 and params['polarity_score'] <= 1:
            shared.processing_message = random.choice(list(params['thinking_emotes_positive_polarity']))
        if params['dream_mode'] == 1:
            print("Setting dream mode processing message.")
            shared.processing_message = "Taking a moment to save Long Term Memories..."
    

    character_name = state["name2"].lower().strip()
    databasefile = os.path.join(databasepath, character_name + "_sqlite.db")
    persona = Persona(databasefile)
    current_time = datetime.now()
    n = 24
    past_time = current_time - timedelta(hours=n)
    past_time_str = past_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    emotions_data = persona.get_emotions_timeframe(past_time_str)
    if params['verbose'] == True:
        print("---Emotions Data from DB:" + str(emotions_data))
    polarity_total = 0
    polarity_len = len(emotions_data)
    for data in emotions_data:
        polarity_total = polarity_total + data['average_polarity']
    if polarity_len != 0:
        average_polarity = polarity_total/polarity_len
        bot_current_polarity = average_polarity
        params['polarity_score'] = average_polarity
        string = "[DTime=" + str(current_time) + "][24hour Average Polarity Score=" + str(average_polarity) + "]" + string
    else:
        string = "[DTime=" + str(current_time) + "]" + string
    
    if params['verbose'] == True:
        print("Bot_prefix_modifer" + str(string))
    

    return string



def input_modifier(string, state, is_chat=False):
    """
    In default/notebook modes, modifies the whole prompt.

    In chat mode, it is the same as chat_input_modifier but only applied
    to "text", here called "string", and not to "visible_text".
    """
    #vars
    character_name = str(state["name2"].lower().strip())
    databasefile = os.path.join(databasepath, character_name + "_sqlite.db")
    stm = ShortTermMemory(databasefile)
    
    if params['verbose'] == True:
        print("---------SHARED VAR----------------")
        #print(shared.settings)
        print("/////////--------SHARED VAR----------------")
        print("bot_current_polarity defined in state['polarity_score']:" + str(params['polarity_score']))
        print(params['thinking_emotes_neutral_polarity'])

    commands_output = None    
    #used for processing [command]'s input by the user.
    if params['dream_mode'] == 0:
        handler = CommandHandler(databasefile)
        commands_output = handler.process_command(string)
        if params['verbose'] == True:
            print("---------COMMANDS OUTPUT----------------")
            print(commands_output)
            print("/////////--------COMMANDS OUTPUT----------------")

        #STM Save of user input.
        people = state['name1'].strip() + " and " + state["name2"].strip()
        is_roleplay = params['is_roleplay']
        initiated_by_name = state['name1'].strip()
        print("String Length:" + str(len(string)))
        if len(string) != 0:
            if params['memory_active'] == True:
                stm.save_memory(string, people, memory_type='short_term', initiated_by=initiated_by_name, roleplay=is_roleplay)
        
        #inserts the qdrant vector db results from the previous bot reply and the current input.
        collection = state['name2'].strip()
        username = state['name1'].strip()
        verbose = params['verbose']
        ltm_limit = params['ltm_limit']
        address = params['qdrant_address']
        ltm = LTM(collection, verbose, ltm_limit, address=address)
        long_term_memories = ltm.recall(string)
        if params['verbose'] == False:
            print("--------------User Line Memories---------------------------")
            print(long_term_memories)
            print("---------------End User Line Memories--------------------------")
            print("--------------Bot Line Memories---------------------------")
            print(bot_long_term_memories)
            print("---------------Bot User Line Memories--------------------------")
        if len(bot_long_term_memories) > 100:
            print("Adding Bot LTM")
            if params['memory_active'] == True:
                string = string + str(bot_long_term_memories)
        if len(long_term_memories) > 100:
            print("Adding User LTM")
            if params['memory_active'] == True:
                string = string + str(long_term_memories)    
        if len(commands_output) > 5:
            print("Adding Commands")
            print(str(commands_output))
            string = string + str(commands_output)    
    
    return string


def output_modifier(string, state, is_chat=False):
    """
    Modifies the LLM output before it gets presented.

    In chat mode, the modified version goes into history['visible'],
    and the original version goes into history['internal'].
    """
    
    character_name = state["name2"].lower().strip()
    databasefile = os.path.join(databasepath, character_name + "_sqlite.db")
    
    commands_output = None    
    #used for processing [command]'s input by the user.
    if params['dream_mode'] == 0:
        #handle [command]'s from the bot
        handler = CommandHandler(databasefile)
        commands_output = handler.process_command(string)
    
        #STM Save of user input.
        people = state['name1'].strip() + " and " + state["name2"].strip()
        is_roleplay = params['is_roleplay']
        initiated_by_name = state['name2'].strip()
        stm = ShortTermMemory(databasefile)
        if params['memory_active'] == True:
            stm.save_memory(string, people, memory_type='short_term', initiated_by=state['name2'].strip(), roleplay=is_roleplay)
        
        #Long-Term-Memory Insert
        #uses the last bot reply and adds it to the input.
        collection = state['name2'].strip()
        username = state['name1'].strip()
        verbose = params['verbose']
        ltm_limit = params['ltm_limit']
        address = params['qdrant_address']
        ltm = LTM(collection, verbose, ltm_limit, address=address)
        bot_long_term_memories = ltm.recall(string)
        if verbose == True:
            print("--------------Bot Line Memories---------------------------")
            print(bot_long_term_memories)
            print("---------------Bot User Line Memories--------------------------")    
        
    if params['dream_mode'] == 0:
        #add the output of commands
        if len(commands_output) > 0:
            string = string + str(commands_output)    
    
    if params['verbose'] == True:
        print("----------STATE--------------")
        print(state)
        print("----------END STATE-------------")

    return string


def custom_generate_chat_prompt(user_input, state, **kwargs):
    """
    Replaces the function that generates the prompt from the chat history.
    Only used in chat mode.
    """

    '''
    This is the main Dream mode that takes STM and saves to LTM. Right now
    it uses the current loaded model, so generation when LTM's are being 
    saved is a bit longer. 
    '''
    if params['memory_active'] == True:
        character_name = state["name2"].lower().strip()
        params['current_persona'] = character_name
        databasefile = os.path.join(databasepath, character_name + "_sqlite.db")
        dream = Dream(databasefile)
        stm_user = ShortTermMemory(databasefile)
        #this should remain around 10 or so so that the conversation flow is recorded. But things happen.

        mems_to_review = dream.get_short_term_memories_not_indexed(100)
        collection = state['name2'].strip()
        username = state['name1'].strip()
        verbose = params['verbose']
        ltm_limit = params['ltm_limit']
        address = params['qdrant_address']
        ltm = LTM(collection, verbose, ltm_limit, address=address)

        print("Len of not indexed mems:" + str(len(mems_to_review)))
        

        if len(mems_to_review) > int(params['ego_summary_limit']):
            print("--------------------------------------Enough memories for a dream...")
            mems_to_review = dream.get_short_term_memories_not_indexed(int(params['ego_summary_limit']))
            params['dream_mode'] = 1
            bot_dream_persona = "Ego:[A subconscious mind of an Artificial Intelligence, designed to process and summarize information from various sources. It focuses on understanding the main topics discussed and extracting key points made. By analyzing data provided by other parts of the AI's system, Ego can identify patterns and themes, enabling it to generate comprehensive summaries even when faced with large amounts of information.]"
            
            thinking_statement = "Generate a summary of the main topics discussed. <START>"
          
            # Process each memory from mems_to_review and store all variables for long-term memory storage
            '''
            #0 id
            1 "memory_text"
            2 "DateTime"
            3 "people"
            
            4 "memory_type"
            5 "initiated_by" 
             6"roleplay"
             7"saved_to_longterm"
            '''
            people = []
            memory_text = []
            dream_check = 0
            for row in mems_to_review:
                #print("Row:" + str(row))
                # Append the memory text with initiator's name to memory_text list
                if int(row[6]) == 0:
                    roleplay = False
                if int(row[6]) == 1:
                    roleplay = True
                if roleplay == True:
                    memory_text.append(f"{row[5]}: {row[1]} [Is_roleplay:{roleplay}]")
                else:
                    memory_text.append(f"{row[5]}: {row[1]}")
                
                #print("MEMORY TEXT:")
                #print(str(memory_text))
                # Store people and other variables from the memory data
                people.append(row[3])

                #todo connect to emotions database and pull out emotions and thoughts.

            # Print a summary of all memories for reference
            #print("MEMORIES:" + str(mems_to_review))

            unique_memories = []
            for memory in memory_text:
                if memory not in unique_memories:
                    unique_memories.append(memory)

            input_to_summarize = '\n\n'.join(unique_memories)
            #print("String:" + string)

            unique_people = []
            for names in people:
                if names not in unique_people:
                    unique_people.append(names)

            input_to_summarize = input_to_summarize + "(A conversation between " + str(unique_people) + " )"
            if params['use_thinking_emotes'] == True:
                shared.processing_message = "Taking a moment to save long-term memories..."
            
            question = bot_dream_persona + "[MEMORY:{'" + input_to_summarize + "'}] " + thinking_statement
            if params['verbose'] == True:
                print('-----------memory question-----------')
                print(question)
                print('-----------/memory question-----------')
            response_text = []
            
            for response in generate_reply(question, state, stopping_strings='"<END>"', is_chat=False, escape_html=False, for_ui=False):
                #print(str(response))
                response_text.append(response) 
                

            
            #print("--------GENERATE REPLY---------------------------------------------------------------")
            
            
            #check the ltm to make sure the response from the llm did not go wacky. 
            #need to think about the best way to check the response. For now at least check 
            #if the llm returned something more then 100 chars.
            #print("Dream Length Check:" + str(len(response_text[-1])))
            if len(str(response_text[-1])) > 100:
                dream_check = 1


            #print("Dream Check:" + str(dream_check))

            if dream_check == 1:
                for row in mems_to_review:
                    #print("Updating memory to saved to LTM." + str(row[0]))
                    stm_user.update_mem_saved_to_longterm(row[0])
            
            #assume the string is the summary of the memories.
            if verbose == True:
                print("----------Memory Summary to save--------------")
                print(str(response_text))
                print("----------")
                print(len(response_text))
                print("----------END Memory Summary to save-------------")
            if dream_check == 1:
                now = datetime.utcnow()
                tosave = str(response_text[-1])
                botname = "Ego"
                doc_to_upsert = {'username': botname,'comment': tosave,'datetime': now}
                ltm.store(doc_to_upsert)
            params['dream_mode'] = 0
        
    result = chat.generate_chat_prompt(user_input, state, **kwargs)
    return result

def custom_css():
    """
    Returns a CSS string that gets appended to the CSS for the webui.
    """
    full_css=''
    #use new scrollbars on main body
    
    full_css+=open(memoir_css, 'r').read()
        
        
    return full_css

def custom_js():
    """
    Returns a javascript string that gets appended to the javascript
    for the webui.
    """
    full_js=''
    #use new scrollbars on main body
    
    full_js+=open(memoir_js, 'r').read()
        
        
    return full_js

def setup():
    """
    Gets executed only once, when the extension is imported.
    """
    #ubuntudockerfile = os.path.join(current_dir, "ubuntu-docker-compose.yml")
    qdrantdockerfile = os.path.join(current_dir, "qdrant-docker-compose.yml")
        
    # run the service
    '''
    try:
        docker_ubuntu_container = DockerClient(compose_files=[ubuntudockerfile])
        docker_ubuntu_container.compose.up(detach=True)
            
        print(f"Running the ubuntu docker service...you can modify this in the ubuntu-docker-compose.yml: {ubuntudockerfile}")
    except Exception as e:
        print(f": Error {ubuntudockerfile}: {e}")
    '''
    try:
        docker_qdrant = DockerClient(compose_files=[qdrantdockerfile])
        docker_qdrant.compose.up(detach=True)
            
        print(f"Running the docker service...you can modify this in the docker-compose.yml: {qdrantdockerfile}")
    except Exception as e:
        print(f": Error {qdrantdockerfile}: {e}")
    pass


def update_dreammode():
    print("-----Params-----")
    print(str(params))
    pass


def _get_current_memory_text() -> str:
    available_characters = utils.get_available_characters()

    info = str(available_characters)
    return info

def delete_everything():
    print("Deleting Everything!")
    if params['current_selected_character'] == None:
        print("No persona selected.")
    else:
        #print("Deleting" + str(character_name))
        character_name = params['current_selected_character']
        databasefile = os.path.join(databasepath, character_name + "_sqlite.db")
        ltm = LTM(character_name, params['verbose'], params['ltm_limit'], address=params['qdrant_address'])
        ltm.delete_vector_db()
        utils.delete_file(databasefile)
        
    pass



def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.

    To learn about gradio components, check out the docs:
    https://gradio.app/docs/
    """

    with gr.Accordion("Memoir+ v.001"):
        with gr.Row():
            gr.Markdown(textwrap.dedent("""
        - If you find this extension useful, <a href="https://www.buymeacoffee.com/brucepro">Buy Me a Coffee:Brucepro</a>
        - For feedback or support, please raise an issue on https://github.com/brucepro
        """))

            
        with gr.Row():
            ltm_limit = gr.Slider(
                1, 100,
                step=1,
                value=params['ltm_limit'],
                label='Long Term Memory Result Count (How many memories to return from LTM into context. Does this number for both bot memories and user memories. So at 5, it recovers 10 memories.)',
                )
            ltm_limit.change(lambda x: params.update({'ltm_limit': x}), ltm_limit, None)
        with gr.Row():
            ego_summary_limit = gr.Slider(
                1, 100,
                step=1,
                value=params['ego_summary_limit'],
                label='Number of Short Term Memories to use for Ego Summary to LTM. How long it waits to process STM to turn them into LTM. If you use too big of a number here when processing LTM it may take some time.',
                )
            ego_summary_limit.change(lambda x: params.update({'ego_summary_limit': x}), ego_summary_limit, None)
        
        with gr.Row():
            cstartdreammode = gr.Button("List Params in debug window")
            cstartdreammode.click(lambda x: update_dreammode(), inputs=cstartdreammode, outputs=None)
        with gr.Row():
            activate_narrator = gr.Checkbox(value=params['activate_narrator'], label='Activate Narrator to use during replies that only contain emotes such as *smiles* (Not Implemented yet.)')
            activate_narrator.change(lambda x: params.update({'activate_narrator': x}), activate_narrator, None)
            activate_roleplay = gr.Checkbox(value=params['is_roleplay'], label='Activate Roleplay flag to tag memories as roleplay (Still experimental. Useful for allowing the bot to understand chatting vs roleplay experiences.)')
            activate_roleplay.change(lambda x: params.update({'is_roleplay': x}), activate_roleplay, None)
            activate_memory = gr.Checkbox(value=params['memory_active'], label='Uncheck to disable the saving of memorys.')
            activate_memory.change(lambda x: params.update({'memory_active': x}), activate_memory, None)
        with gr.Row():
            use_thinking_emotes_ckbox = gr.Checkbox(value=params['use_thinking_emotes'], label='Uncheck to disable the thinking emotes.')
            use_thinking_emotes_ckbox.change(lambda x: params.update({'use_thinking_emotes': x}), use_thinking_emotes_ckbox, None)
        with gr.Row():
            available_characters = utils.get_available_characters()
            character_list = gr.Dropdown(
            available_characters, label="Characters available to delete", info="List of Available Characters. Used for delete button.")
            character_list.change(lambda x: params.update({"current_selected_character": x}), character_list, None)
        
            destroy = gr.Button("Destroy all memories/goals/emotion data for selected character", variant="stop")
            destroy_confirm = gr.Button(
                "THIS IS IRREVERSIBLE, ARE YOU SURE?", variant="stop", visible=False
            )
            destroy_cancel = gr.Button("Do Not Delete", visible=False)
            destroy_elems = [destroy_confirm, destroy, destroy_cancel]
            # Clear memory with confirmation
        destroy.click(
            lambda: [gr.update(visible=True), gr.update(visible=False), gr.update(visible=True)],
            None,
            destroy_elems,
        )
        destroy_confirm.click(
            lambda: [gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)],
            None,
            destroy_elems,
        )
        destroy_confirm.click(lambda x: delete_everything(), inputs=destroy_confirm, outputs=None)
        destroy_cancel.click(
            lambda: [gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)],
            None,
            destroy_elems,
        )
