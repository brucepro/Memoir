"""
script.py - main entrance of the script into the Text Generation Web UI system extensions

Memoir+ a persona extension for Text Gen Web UI. 
MIT License

Copyright (c) 2025 brucepro, corbin-hayden13
"""

import os
import gradio as gr
import textwrap
from datetime import datetime, timedelta 
from modules import chat, utils
from modules.text_generation import (
    generate_reply,
)
import json
from python_on_whales import DockerClient

from extensions.Memoir.commandhandler import CommandHandler
from extensions.Memoir.chathelper import ChatHelper
from extensions.Memoir.memory.short_term_memory import ShortTermMemory
from extensions.Memoir.big_memory.big_memory import LTM, RagDataMemory
from extensions.Memoir.memory.dream import Dream
from extensions.Memoir.persona.persona import Persona
from extensions.Memoir.commands.file_load import File_Load

#globals
current_dir = os.path.dirname(os.path.abspath(__file__))
memoir_js = os.path.join(current_dir, "memoir.js")
memoir_css = os.path.join(current_dir, "memoir.css")
databasepath = os.path.join(current_dir, "storage/sqlite/")
params_txt = os.path.join(current_dir, "memoir_config.json")


def save_params_to_file(arg):
    global params_txt

    params_txt = os.path.join(current_dir, "memoir_config.json") 
    with open(params_txt, 'w') as f:
        json.dump(params, f)


def load_params_from_file(params_json):
    if os.path.exists(params_json):
        with open(params_json) as config_file:
            config = json.load(config_file)
    else:
        config = {}
    return config


# Load the params dictionary from the confignew.json file
params = load_params_from_file(params_txt)


def memory_insert():
    """
    Handles the insertion of the memories into the chat. 
    """
    memory_text = list(params['bot_long_term_memories']) + list(params['user_long_term_memories'])
    params['bot_long_term_memories'] = ""
    params['user_long_term_memories'] = ""
    unique_memories = []
    for memory in memory_text:
        if memory not in unique_memories:
            unique_memories.append(memory)
    if params['verbose']:
        print("--------------Memories---------------------------")
        print(unique_memories)
        print("---------------End Memories--------------------------")
                
        print("Len mem:" + str(len(unique_memories)))
    if len(unique_memories) > 0:
        return "[You remember:" + str(unique_memories) + " ] "
    else:
        return ""  


def rag_insert():
    """
    Handles the insertion of the RAG items into the chat.
    """
    rag_text = list(params['bot_rag_data']) + list(params['user_rag_data'])
    unique_rags = []
    for rag in rag_text:
        if rag not in unique_rags:
            unique_rags.append(rag)
    if len(unique_rags) > 0:
        return "[Augumented Information:" + str(unique_rags) + " ] "
    else:
        return ""


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
    state['ego_persona_name'] = params['ego_persona_name']
    state['ego_persona_details'] = params['ego_persona_details']
    
    state['ego_thinking_statement'] = params['ego_thinking_statement']
    state['memory_active'] = params['memory_active']
    state['qdrant_address'] = params['qdrant_address']
    state['polarity_score'] = params['polarity_score']
    state['current_selected_character'] = params['current_selected_character']
    '''
    Since we are adding to the bot prefix, they tend to get hung up on 
    using the prefix. Good spot to give extra instructions, but we need
    add the stop string. Also when the bot speaks as the user it is annoying,
    so fix for that. Update 8/1/2024 Seems to not be useful anymore and most models are fine without it from my testing.
    '''
    return state


def bot_prefix_modifier(string, state):
    """
    Modifies the prefix for the next bot reply in chat mode.
    By default, the prefix will be something like "Bot Name:".
    """
    character_name = state["name2"].lower().strip()
    params['current_persona'] = state['name2'].strip()
    database_file = os.path.join(databasepath, character_name + "_sqlite.db")
    persona = Persona(database_file)
    current_time = datetime.now()
    datetime_obj = current_time
    date_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    n = 24
    past_time = current_time - timedelta(hours=n)
    past_time_str = past_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    stm_polarity_data: float = float(persona.get_stm_polarity_timeframe(past_time_str))
    bot_current_polarity: float = round(stm_polarity_data, 4)
    params['polarity_score'] = bot_current_polarity
    string = "[DateTime=" + str(date_str) + "][24hour Average Polarity Score=" + str(bot_current_polarity) + "] " + string
    #insert rag into prefix
    if params['botprefix_rag_enabled'] == "Enabled":
        if params['rag_active']:
            string = str(rag_insert()) + string

    #insert memories into prefix.
    if params['botprefix_mems_enabled'] == "Enabled":
        if params['memory_active']:
            string = str(memory_insert()) + string
            #print(string)    
    return string



def input_modifier(string, state):
    """
    In default/notebook modes, modifies the whole prompt.

    In chat mode, it is the same as chat_input_modifier but only applied
    to "text", here called "string", and not to "visible_text".
    """
    #vars
    #we need to pass state to some of our buttons. Need to think of a better way.
    global params

    params['current_persona'] = state['name2'].strip()
    character_name = params["current_persona"].lower()
    database_file = os.path.join(databasepath, character_name + "_sqlite.db")
    stm = ShortTermMemory(database_file)

    #used for processing [command]'s input by the user.
    if params['dream_mode'] == 0:
        handler = CommandHandler(database_file, params)
        commands_output = handler.process_command(string)
        if params['verbose']:
            print("---------COMMANDS OUTPUT----------------")
            print(commands_output)
            print("/////////--------COMMANDS OUTPUT----------------")

        #STM Save of user input.
        people = state['name1'].strip() + " and " + params['current_persona']
        initiated_by_name = state['name1'].strip()
        
        if params['activate_narrator']:
            if ChatHelper.check_if_narration(string):
                initiated_by_name = "Narrator"
                
        if len(string) != 0:
            if params['memory_active']:
                stm.save_memory(string, people, memory_type='short_term', initiated_by=initiated_by_name, roleplay=params['is_roleplay'])
        
        #inserts the qdrant vector db results from the previous bot reply and the current input.
        ltm = LTM(params)
        params['user_long_term_memories'] = ltm.recall(string)
        rag = RagDataMemory(params)
        params['user_rag_data'] = rag.recall(string)
        
        if len(commands_output) > 0:
            string = string + " [" + str(commands_output) + "]"    
        #insert rag into prefix
        if params['botprefix_rag_enabled'] == "Disabled":
            if params['rag_active']:
                string = str(rag_insert()) + string
        #insert memories into prefix.
        if params['botprefix_mems_enabled'] == "Disabled":
            if params['memory_active']:
                string = str(memory_insert()) + string   
        print("--------current context string input modifier---------------")
        print(string)
        print("--------/end context string input modifier---------------")
    return string


def output_modifier(string, state, is_chat=False):
    """
    Modifies the LLM output before it gets presented.

    In chat mode, the modified version goes into history['visible'],
    and the original version goes into history['internal'].
    """
    
    
    character_name = state["name2"].lower().strip()
    params['current_persona'] = state['name2'].strip()
    database_file = os.path.join(databasepath, character_name + "_sqlite.db")
    commands_output = None    
    #used for processing [command]'s input by the user.
    if params['dream_mode'] == 0:
        #handle [command]'s from the bot
        handler = CommandHandler(database_file, params)
        commands_output = handler.process_command(string)
    
        #STM Save of user input.
        people = state['name1'].strip() + " and " + state["name2"].strip()
        is_roleplay = params['is_roleplay']
        initiated_by_name = state['name2'].strip()
        if params['activate_narrator']:
            if ChatHelper.check_if_narration(string):
                #print("STM is a narration")
                initiated_by_name = "Narrator"
         
        stm = ShortTermMemory(database_file)
        if params['memory_active']:
            stm.save_memory(string, people, memory_type='short_term', initiated_by=initiated_by_name, roleplay=is_roleplay)
        
        #Long-Term-Memory Insert
        #uses the last bot reply and adds it to the input.
        ltm = LTM(params)
        params['bot_long_term_memories'] = ltm.recall(string)
        rag = RagDataMemory(params)
        params['bot_rag_data'] = rag.recall(string)
    if params['dream_mode'] == 0:
        #add the output of commands
        if len(commands_output) > 0:
            string = string + str(commands_output)    

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
    global params

    if params['memory_active']:
        character_name = state["name2"].lower().strip()
        params['current_persona'] = state['name2'].strip()
        database_file = os.path.join(databasepath, character_name + "_sqlite.db")
        dream = Dream(database_file)
        stm_user = ShortTermMemory(database_file)
        #this should remain around 10 so that the conversation flow is recorded. But things happen.

        mems_to_review = dream.get_short_term_memories_not_indexed(int(params['ego_summary_limit']))
        ltm = LTM(params)
        

        if len(mems_to_review) >= int(params['ego_summary_limit']):
            print("--------------------------------------Enough memories for a dream...")
            
            params['dream_mode'] = 1
            
            bot_dream_persona = "You are " + str(params['ego_persona_name']) + ": " + str(params['ego_persona_details'])
            
            thinking_statement = str(params['ego_thinking_statement'])
          
            people = []
            memory_text = []
            dream_check = 0
            roleplay_message = ""
            for row in mems_to_review:
                # roleplay = False if row[6] == 0 anyway
                roleplay: bool = False
                if int(row[6]) == 1:
                    roleplay = True
                if roleplay:
                    roleplay_message = "(These memories are part of a roleplay session, note that it was part of a roleplay in the memory summary.)"

                if str(row[5]) == "Narrator":
                    memory_text.append(f"{row[1]}")
                else:
                    memory_text.append(f"{row[5]}: {row[1]}")
                people.append(row[3])

            unique_memories = []
            for memory in memory_text:
                if memory not in unique_memories:
                    unique_memories.append(memory)

            input_to_summarize = '\n\n'.join(unique_memories)
            
            unique_people = []
            for names in people:
                if names not in unique_people:
                    unique_people.append(names)

            input_to_summarize = input_to_summarize + "(A conversation between " + str(unique_people) + " )"
            stm_context = ltm.get_last_summaries(1)
            if len(stm_context) > 0:
                stm_context_string = "[Past Summary Context from last 1 hour:{'" + str(stm_context) + "'} These past summaries will help you better understand the current context.]"
            else:
                stm_context_string = "" 
            
            question = bot_dream_persona + stm_context_string + "[MEMORIES:{'" + input_to_summarize + "'}] " + roleplay_message + thinking_statement
            
            if params['verbose']:
                print('-----------memory question-----------')
                print(question)
                print('-----------/memory question-----------')
            response_text: list = []
            
            for response in generate_reply(question, state, stopping_strings='"<END>","</END>"', is_chat=False, escape_html=False, for_ui=False):
                response_text.append(response) 
            #time.sleep(1)
            if len(str(response_text[-1])) > 100:
                dream_check = 1
                print("Summary passed checking")

            if dream_check == 1:
                for row in mems_to_review:
                    stm_user.update_mem_saved_to_longterm(row[0])

            if params['verbose']:
                print("----------Memory Summary to save--------------")
                print(str(response_text[-1]))
                print("----------")
                print(len(response_text[-1]))
                print("----------END Memory Summary to save-------------")
            if dream_check == 1:
                now = datetime.utcnow()
                tosave = str(response_text[-1]) + " " + str(roleplay_message)
                botname = state['name2'].strip()
                doc_to_upsert = {'username': botname,'comment': str(tosave),'datetime': now, 'people': str(unique_people)}
                if params['verbose']:
                    print("Saving to Qdrant" + str(doc_to_upsert))
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


def try_nondocker_qdrant():
    """
    If you don't want to run Text Generation WebUI in docker, you'll need to fulfill the Qdrant dependency for this
        extension yourself.

    1. Go to https://github.com/qdrant/qdrant/releases and download the latest compiled Qdrant binary
        - Prebuilt binaries come as archive files (.zip, .tar, etc.) from GitHub
    2. Unzip / unpack the binary into "./nondocker_qdrant"
    3. (Optional, decreases load time) Set "qdrant_on_docker" to `false` in `./memoir_config.json`
    4. (Optional) Double check that the "qdrant_address" from `./memoir_config.json` matches the
        `./nondocker_qdrant/nondocker_qdrant_config.yaml` file data and that the port `6333` is being used EVERYWHERE
    5. You're done!
    """
    from extensions.Memoir.nondocker_qdrant.start_nondocker_qdrant import start_qdrant_server
    try:
        start_qdrant_server()

    except Exception as e:
        print(f"Failed to launch qdrant with non-Docker approach: Error - {e}")


def setup():
    """
    Gets executed only once, when the extension is imported.

    If for some reason you can't run docker, the system will work by installing the qdrant binaries 
    https://github.com/qdrant/qdrant/releases
    As long as the server and port match in the memoir_config.json you should be good. Then comment out the docker stuff below or remove this entire function.
    """
    qdrantdockerfile = os.path.join(current_dir, "qdrant-docker-compose.yml")
        
    # run the service
    if params["qdrant_on_docker"]:
        try:
            docker_qdrant = DockerClient(compose_files=[qdrantdockerfile])
            docker_qdrant.compose.up(detach=True)

            print(
                f"Running the docker service...you can modify this in the docker-compose.yml: {qdrantdockerfile} . If you get an error here it is most likely that you forgot to load docker. I recommend docker desktop.")
        except:
            # Try the non-docker approach EVEN IF it's not been set in the memoir_config file
            print("Encountered error running qdrant in Docker, trying non-Docker approach...")
            try_nondocker_qdrant()

    else:
        try_nondocker_qdrant()


def update_dreammode():
    print("-----Params-----")
    print(str(params))
    pass


def deep_dream():
    params['deep_dream'] = 1


def _get_current_memory_text() -> str:
    available_characters = utils.get_available_characters()
    info = str(available_characters)
    return info


def delete_everything():
    global params

    if params['current_selected_character'] is None:
        print("No persona selected.")
    else:
        character_name_lowercase = str(params['current_selected_character']).lower().strip()
        
        database_file = os.path.join(databasepath, character_name_lowercase + "_sqlite.db")
        ltm = LTM(params)
        ltm.delete_vector_db()
        utils.delete_file(database_file)


def load_params_from_file_ui(arg):
    print("--------arg--------")
    print(arg)
    load_params_from_file(params_txt)


def rag_upload_file(file):
    print(file)
    file_path = str(file.name)
    print("********FILEPATH*********")
    print(file_path)
    if params['current_persona'] != "":
        file_load_handler = File_Load(params)
                    
        content = file_load_handler.read_file(file_path)
        print("***********RAG FILE UPLOADED*************")
        print(content)
        print("**************************************")
    else:
        print("Current Persona is not selected, yet. Interact with your agent first. ")

    return 'File inserted into the RAG vector Store.'


def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.

    To learn about gradio components, check out the docs:
    https://gradio.app/docs/
    """
    with gr.Blocks() as memoir_ui:
        with gr.Accordion("Memoir+ v.001"):
            with gr.Row():
                gr.Markdown(textwrap.dedent("""
            - If you find this extension useful, <a href="https://www.buymeacoffee.com/brucepro">Buy Me a Coffee:Brucepro</a> or <a href="https://ko-fi.com/brucepro">Support me on Ko-fi</a>
            - For feedback or support, please raise an issue on https://github.com/brucepro/Memoir
            """))

                save_params_button = gr.Button("Save Settings to File")
                save_params_button.click(save_params_to_file, inputs=save_params_button, outputs=None)
                     

            with gr.Accordion("Memory Settings"):    
                with gr.Row():
                    ltm_limit = gr.Slider(
                        1, 100,
                        step=1,
                        value=params["ltm_limit"],
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
            with gr.Accordion("RAG Settings"):    
                with gr.Row():
                    gr.Markdown(textwrap.dedent("""
                - The RAG system uses the langchain loaders. It saves to a unique collection in the qdrant database called botname_rag_data
                - Commands are [FILE_LOAD=filelocation - this can be on your filesystem or online. Also supports directory loading but that uses the unstructured text loader so isn't as nice as using the specific loaders like .pdf, .epub etc.]
                - [GET_URL=url,output] - The output field will output the contents to the bot context. 
                - Both commands output to the current context and save to the RAG system. Will work on setting a flag for this later. 
                - The file box below will load the file directly to the RAG vector database (It will not load it to context, will add a checkbox for that feature soon.)
                """))
                

                with gr.Row():
                    last_updated = gr.Markdown()
                    file_input = gr.File(label='Input file')
                    update_file = gr.Button('Load data')
                    # Assuming `True` means "full" in `show_progress` context
                    update_file.click(rag_upload_file, [file_input], last_updated, show_progress="full")
                with gr.Row():
                    rag_limit = gr.Slider(
                        1, 100,
                        step=1,
                        value=params["rag_limit"],
                        label='RAG Result Count (How many items to return from the RAG into context. Does this number for both bot reply and user reply. So at 5, it recovers 10 rag items.)',
                        )
                    rag_limit.change(lambda x: params.update({'rag_limit': x}), rag_limit, None)
                with gr.Row():
                    rags_in_bot_prefix = gr.Radio(
                            choices={"Enabled": "true", "Disabled": "false"},
                            label="RAG in Bot Prefix (Saves context)",
                            value=params['botprefix_rag_enabled'],
                        )
                    rags_in_bot_prefix.change(lambda x: params.update({'botprefix_rag_enabled': x}), rags_in_bot_prefix, None)
                    rag_active = gr.Checkbox(value=params['rag_active'], label='Uncheck to disable the rag system.')
                    rag_active.change(lambda x: params.update({'rag_active': x}), rag_active, None)
            with gr.Accordion("Debug"):    
                with gr.Row():
                    cstartdreammode = gr.Button("List Params in debug window")
                    cstartdreammode.click(lambda x: update_dreammode(), inputs=cstartdreammode, outputs=None)
                         
                with gr.Row():
                    ego_persona_name_textbox = gr.Textbox(show_label=False, value=params['ego_persona_name'], elem_id="ego_persona_name_textbox")
                    ego_persona_name_textbox.change(lambda x: params.update({'ego_persona_name': x}), ego_persona_name_textbox, None)
                    ego_persona_details_textarea = gr.TextArea(label="Ego Persona details", value=params['ego_persona_details'], elem_id="ego_persona_details")
                    ego_persona_details_textarea.change(lambda x: params.update({'ego_persona_details': x}), ego_persona_details_textarea, None)
                    ego_thinking_statement_textbox = gr.TextArea(label="Ego Thinking Statement", value=params['ego_thinking_statement'], elem_id="ego_thinking_statement_textbox")
                    ego_thinking_statement_textbox.change(lambda x: params.update({'ego_thinking_statement': x}), ego_thinking_statement_textbox, None)
                with gr.Row():
                    mems_in_bot_prefix = gr.Radio(
                        choices={"Enabled": "true", "Disabled": "false"},
                        label="Memories in Bot Prefix (Saves context)",
                        value=params['botprefix_mems_enabled'],
                    )
                    mems_in_bot_prefix.change(lambda x: params.update({'botprefix_mems_enabled': x}), mems_in_bot_prefix, None)
            with gr.Accordion("Settings"):
                with gr.Row():
                    activate_narrator = gr.Checkbox(value=params['activate_narrator'], label='Activate Narrator to use during replies that only contain emotes such as *smiles*')
                    activate_narrator.change(lambda x: params.update({'activate_narrator': x}), activate_narrator, None)
                    activate_roleplay = gr.Checkbox(value=params['is_roleplay'], label='Activate Roleplay flag to tag memories as roleplay (Still experimental. Useful for allowing the bot to understand chatting vs roleplay experiences.)')
                    activate_roleplay.change(lambda x: params.update({'is_roleplay': x}), activate_roleplay, None)
                    activate_memory = gr.Checkbox(value=params['memory_active'], label='Uncheck to disable the saving of memorys.')
                    activate_memory.change(lambda x: params.update({'memory_active': x}), activate_memory, None)
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

