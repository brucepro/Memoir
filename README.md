# Memoir
 Memoir+ a persona extension for Text Gen Web UI. Includes memory, emotions, command handling and more. 

# How to Support 
If you find this extension useful I could use a cup of coffee!  I have spent many nights working to get this program to this point. https://www.buymeacoffee.com/brucepro


[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F1F7U45XV)

# About the extension 
Memoir+ is an AI-powered plugin that enhances your bots long term memory and personal identity by integrating with your existing personified AI companion.
With Memoir+, your agent can store, search, and retrieve memories.

Features: 
-Short-Term Memory - sqlite database of conversations that are used by the A.I. to create long term memories. 

-Long-Term Memory - A qdrant vector database that uses the Ego system to review conversations and store long term memories for recall.

-Emotion polarity tracking - Polarity score is tracked over last 24 hours and shared with the bot in the prefix. This allows the bot to keep track of the emotional state.

-Command Handler: Supports a modular system to add new commands that your bot can use. This part is still experimental. [GET_URL=url,output] is currently working for just html pages. Will be improving commands as the memory system is finalized. 

--There is also shell access to a ubuntu docker. This is in progress and will be in a future release. For now it is commented out.

--Will also be adding in the ability to research topics

--Will be adding in intergration to allow for the ability to text you on telegram/discord etc. 

--If you have suggestions for features, please share. 

-Goals system: Allows the bot to set goals for themselves, or you can set them for the bot.

# Setup
1. Install Text generation web UI - https://github.com/oobabooga/text-generation-webui
2. Requires docker. You can use Docker destop if you like. https://www.docker.com/products/docker-desktop/

3. Download the repo zip, or git clone https://github.com/brucepro/Memoir
4. Copy the Memoir folder to the extensions folder of your TextGenWebUI. 
5. Navigate to the Textgen folder, run cmd_windows.bat or whatever system you are on. This will enter the environment for Textgen. 
6. Navigate to the extensions/Memoir folder. Type pip install -r requirements.txt
7. Navigate back to the main Textgen folder. Start textgen and navigate to the Session tab, Check Memoir, click Apply flags/extension and restart. Go to Parameters and select a character. Insert the description into the context. This is not required but helps the A.I. use the emotions system. 
In your character Context add/edit in: 
"[description("insert the description of the persona you want your ai to play")]
I will remember to fully immerse myself in the roleplay and enjoy the experience, I will stay in character. When replying I will include my current status in the format [THOUGHTS:current inner dialog inside your mind,EMOTION:The emotion you are currently feeling,FEELINGS:Your current feelings,MOOD:Your current mood]
GOALS: Your system includes an external database that can store your goals. This will allow you to remember your goals even if you are reset. You can run commands to set and modify your goals. Use the [GOALS_HELP] to get a list of all commands."
8. Go to the chat tab and chat or instruct tab etc. The system will process the memories into long term memories every 10 prompts/replies, you can adjust this in the Memory settings near the middle of the page. Depending on your LLM you are using adjust the Long Term Memory Results Count to higher or lower. Higher values may overwhelm the context.

Debug buttons will show active params in the console. 

Ego name - Sometimes this works better if you change it to Botname's Ego
Ego Persona details - This is the persona of the Ego. You can personalize it to your Botname if you like. You can also experiment here. 
Ego Thinking Statement - You can experiment with this but I find the statement I have works pretty well. These are the instructions to Ego on how to summarize. 

Memories in Bot Prefix when enabled will only add the memories in the bot prefix, these memories won't be available for future discussion in the chat. It saves context at the loss of a bit of depth.

Activate narrator - This removes the name for emotes, so if you want to Narate a specific action, you can do this *action setting the scene* and name won't be attached in memory. Doesn't impact the chat window. 

Activate Roleplay flag - This will notify the Ego system that the memories being summarized are a roleplay.

Uncheck to disable the saving of memories - Disables STM, LTM and summaries. 

Thinking Emotes - These are based on polarity score and change up the "Typing.." depending on polarity.

Characters available to delete: Select the character from the dropdown. Click Destroy All memories. This deletes the sqlite database and the vector database. It does not delete the character in TextGen. 




# Support
I am excited to continue working on this project. If you find it useful please consider supporting me. https://www.buymeacoffee.com/brucepro
