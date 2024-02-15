# Memoir+: Enhanced Persona Extension for Text Generation Web UI

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
- **Command Handling:** A modular system for executing custom commands within the AI environment.
- **Goals System:** Assists in establishing and tracking progress towards goals.

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
- **Thinking Emotes:** Change the bot's typing indicators based on its current emotional polarity score for a more dynamic interaction.

### Character Management

- **Delete Characters:** Efficiently manage and delete character data, including all associated memories and emotional data.

## Future Development

- **Docker/Shell Access:** Upcoming feature for advanced control and system automation.
- **Topic Research:** Enhanced capabilities for information gathering and utilization.
- **Messaging Integrations:** For direct notifications and updates across various messaging platforms.

## Installation

1. Install the Text Generation Web UI as per instructions on [GitHub](https://github.com/oobabooga/text-generation-webui).
2. Get Docker Desktop from [Docker](https://www.docker.com/products/docker-desktop/).
3. Clone the Memoir repository: `git clone https://github.com/brucepro/Memoir`.
4. Move the Memoir folder into the extensions directory of your TextGenWebUI installation.
5. In the Memoir folder, execute `pip install -r requirements.txt` to install dependencies.

## Usage

Configure your AI character's description and goals in the TextGen UI. Engage in conversation, and watch as Memoir begins to store and utilize the generated memories, enhancing the interaction with your AI.

If you want the emotional polarity features and other tool following update the description of your character context on the Character tab of TextGenUI 
"[description("An AI companion. *Add anything you like here or copy from your character card. Does support a full character card, but I find simple is better.*")] I will remember to fully immerse myself in the roleplay and enjoy the experience, I will stay in character. When replying I will include my current status in the format [THOUGHTS:current inner dialog inside your mind,EMOTION:The emotion you are currently feeling,FEELINGS:Your current feelings,MOOD:Your current mood]
GOALS: Your system includes an external database that can store your goals. This will allow you to remember your goals even if you are reset. You can run commands to set and modify your goals. Use the [GOALS_HELP:1] to get a list of all commands. 
<START> "
## Support

If Memoir adds value to your AI experience and you'd like to show your appreciation, consider supporting the project:

- [Buy me a coffee](https://www.buymeacoffee.com/brucepro)
- [Ko-fi](https://ko-fi.com/F1F7U45XV)

## Contributing

Contributions, suggestions, and feedback are always welcome. Please submit issues or pull requests on GitHub, or contact us directly with your ideas and suggestions.

## License

Memoir is made available under the MIT License. For more details, see the LICENSE file in the repository.
