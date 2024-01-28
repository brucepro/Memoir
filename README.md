# Memoir
 Memoir+ a persona extension for Text Gen Web UI. Includes memory, emotions, command handling and more.

# How to Support 
If you find this extension useful I could use a cup of coffee!  I have spent many nights working to get this program to this point. https://www.buymeacoffee.com/brucepro

# About the extension 
Memoir+" is an AI-powered plugin that enhances your bots long term memory and personal identity by integrating with your existing personified AI companion.
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
Install requirements.txt 
Requires docker destop etc if on windows.

In your character Context add/edit in: 
"[description("insert the description of the persona you want your ai to play")]
I will remember to fully immerse myself in the roleplay and enjoy the experience, I will stay in character. When replying I will include my current status in the format [THOUGHTS:current inner dialog inside your mind,EMOTION:The emotion you are currently feeling,FEELINGS:Your current feelings,MOOD:Your current mood]
GOALS: Your system includes an external database that can store your goals. This will allow you to remember your goals even if you are reset. You can run commands to set and modify your goals. Use the [GOALS_HELP] to get a list of all commands."

# Support
I am excited to continue working on this project. If you find it useful please consider supporting me. https://www.buymeacoffee.com/brucepro
