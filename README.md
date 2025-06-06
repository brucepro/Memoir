# Memoir+: Enhanced Persona Extension for Text Generation Web UI
![Image of an android writing in a journal with futuristic city out of window: Generated by Dalle](https://raw.githubusercontent.com/brucepro/Memoir/main/images/ai_gen_memoir.jpg)

Important: I recommend you go to the qdrant dashboard: http://localhost:6333/dashboard and create and download a snapshot of your agents vector store. This will allow you to restore in case something happens where the docker zaps it. Next release has a few features to fix this, but good to have the backup.

## Introduction

Memoir is an AI-powered plugin designed to enrich your existing AI companions within the Text Generation Web UI. With advanced memory capabilities and emotional intelligence, Memoir transforms your interactions with AI into a more nuanced and human-like experience.

## Table of Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [Configuration](#configuration)
- [Future Development](#future-development)
- [Installation](#installation)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)
- [License](#license)

## Key Features

- **Short-Term Memory:** Stores recent conversations for enhanced contextual awareness.
- **Long-Term Memory:** Utilizes a vector database for creating and recalling durable memories. (You can manage and edit entries on the qdrant dashboard: http://localhost:6333/dashboard )
- **Emotion Tracking:** Monitors and adjusts the AI's emotional responses over time.
- **Command Handling:** A modular system for executing custom commands within the AI environment. [GET_URL=url,output]
- **RAG System:** Ability to ingest urls and files. Uses langchain community loaders for supported filetypes. For .epub support you may need to install (https://github.com/jgm/pandoc)
Command Structure:

YES:

[FILE_LOAD=https://arxiv.org/pdf/2402.10790.pdf]

[FILE_LOAD=C:/pdfs/2402.10790.pdf]

[FILE_LOAD=C:/pdfs/] - Will use unstructured loader. Better to use the pdf loader.

[GET_URL=https://www.npr.org/sections/world/, output]

NO:

[FILE_LOAD=https://www.npr.org/sections/world/] - Have not added the logic for no file extension on urls for file loader yet, use the [GET_URL=url,output] command.




## Configuration

Memoir offers detailed configuration options for personalizing your AI's memory and personality traits:

### Memory Settings

- **Long Term Memory Result Count:** Adjust the number of memories to incorporate into the current context for a richer interaction.
- **Short Term Memory Processing Interval:** Set the frequency of converting short-term to long-term memories to optimize performance and relevance.

### Ego Configuration

- **Ego Name:** Customize the ego name to correspond with your AI's identity, enhancing recognition and personalization.
- **Ego Persona Details:** Craft a detailed persona for your AI's subconscious mind to guide its summarization and understanding of conversations.
- **Ego Thinking Statement:** Direct your AI on how to synthesize conversations and identify key points, allowing for creative experimentation.

### Memory in Bot Prefix

- **Enable/Disable Saving Context:** Control whether memories are added to the bot's prefix, trading off between preserving context and conversational depth.

### Narration and Roleplay

- **Activate Narrator:** Omit character names from emotes to better set the scene during narrative passages.
- **Activate Roleplay Flag:** Indicate to the system when it is summarizing roleplay sessions to adjust the handling of memories.

### Debugging and Memory Management

- **Memory Saving Toggle:** Swiftly enable or disable memory recording for troubleshooting or adjusting privacy settings.

### Character Management

- **Delete Characters:** Efficiently manage and delete character data, including all associated memories and emotional data.

## Future Development

- **Docker/Shell Access:** Upcoming feature for advanced control and system automation.
- **Topic Research:** Enhanced capabilities for information gathering and utilization.
- **Messaging Integrations:** For direct notifications and updates across various messaging platforms.

## Installation

1. Install the Text Generation Web UI as per instructions on [GitHub](https://github.com/oobabooga/text-generation-webui).
2. Get Docker Desktop from [Docker](https://www.docker.com/products/docker-desktop/). (If for some reason you cannot load docker, you can bypass it by installing qdrant binary (https://github.com/qdrant/qdrant/releases) You can then comment out the docker loads in startup of script.py)
3. Clone the Memoir repository: `git clone https://github.com/brucepro/Memoir`.
4. Move the Memoir folder into the extensions directory of your TextGenWebUI installation (Make sure it is named 'Memoir').
5. Run the update_wizard bat for your OS. Select B) Install/update extensions requirements, Select Memoir from the list (or if you are familiar with terminal/CMD - from TextGenWebUI/extensions/Memoir folder, run `pip install -r requirements.txt --upgrade`).
6. Restart Text Generation Web UI, goes to 'Session' tab - checked on Memoir, then 'Apply flags/extensions and restart'.
7. Make sure Memoir extension load successfully from Text Generation Web UI console.

For current text gen run: portable_env\python.exe -m pip install -r extensions\Memoir\requirements.txt
## Usage

Configure your AI character's description if you like in the TextGen UI character tab. Engage in conversation, and watch as Memoir+ begins to store and utilize the generated memories, enhancing the interaction with your AI.
 
## Support

If Memoir adds value to your AI experience and you'd like to show your appreciation, consider supporting the project:

- [Buy me a coffee](https://www.buymeacoffee.com/brucepro)
- [Ko-fi](https://ko-fi.com/F1F7U45XV)

## Contributing

Contributions, suggestions, and feedback are always welcome. Please submit issues or pull requests on GitHub, or contact us directly with your ideas and suggestions.

## License

Memoir is made available under the MIT License. For more details, see the LICENSE file in the repository.
