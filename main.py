import asyncio
import aiohttp
import json
from rich.console import Console
from rich.theme import Theme
from rich.text import Text
from rich.panel import Panel
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Set up a Rich theme
theme = Theme({
    "user": "#87ceeb",  # Sky blue
    "ai": "#87ceeb",  # Lime green  #32cd32
    "border": "#87ceeb",  # Bright red
    "panel.title": "#ffa07a",  # Bright orange
    "panel.border": "#66d9ef",  # Pastel blue
    "error": "bold red"
})

# Create a Rich console
console = Console(theme=theme)

#model = "meta-llama/llama-3.1-8b-instruct:free"
model = "nousresearch/hermes-3-llama-3.1-405b"

# Default system prompt
default_system_prompt = "You are an AI chat assistant. Respond to the user's queries."

# Clear the console
os.system('cls' if os.name == 'nt' else 'clear')

# Start a Rich console session
welcome_panel = Panel(
    f"""

[ai]Model: {model}[/ai]

[border]Available commands:[/border]

• [border]/help[/border] - Show list of available commands
• [border]/reset[/border] - Reset the conversation history
• [border]/save[/border] - Save the conversation history to a file
• [border]/quit[/border] - Quit the chat session

[border]How it works:[/border]

• This code uses the OpenRouter API to generate responses to user queries.
• It takes a user query as input and generates two responses:
    - One response is based on a default system prompt, which is a generic prompt that doesn't take into account the user's previous queries.
    - The second response is based on a user-entered system prompt, which is a prompt that the user can customize to fit their specific needs.
• If the user doesn't enter a system prompt, the code will use the default system prompt to generate both responses.

[border]Default System Prompt:[/border]

{default_system_prompt}

[border]Enter a system prompt to customize the AI's responses. If no prompt is entered, the default system prompt will be used.[/border]

""",
    title="[ai]Open Router Prompt Companion[/ai]",
    border_style="border"
)
console.print(welcome_panel)


# Prompt for system input
system_input = console.input("Enter a system prompt (optional): ")

# Print the user-entered system prompt inside the box
if system_input:
    system_panel = Panel(system_input, title="[border]User-Entered System Prompt[/border]", border_style="border")
    console.print(system_panel)
else:
    system_panel = Panel(default_system_prompt, title="[border]Default System Prompt[/border]", border_style="border")
    console.print(system_panel)

class ChatSession:
    def __init__(self):
        self.default_conversation_history = []
        self.user_conversation_history = []
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.full_conversation_history = []

    async def get_api_response(self, session, data):
        async with session.post(self.url, headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}, json=data) as response:
            return await response.json()

    async def main(self):
        async with aiohttp.ClientSession() as session:
            if system_input:
                # Initialize conversation history for user-entered system prompt
                self.user_conversation_history.append({"role": "system", "content": system_input})

                # Initialize conversation history for default system prompt
                self.default_conversation_history.append({"role": "system", "content": default_system_prompt})
            else:
                # Initialize conversation history for default system prompt
                self.default_conversation_history.append({"role": "system", "content": default_system_prompt})

                # Initialize conversation history for user-entered system prompt
                self.user_conversation_history.append({"role": "system", "content": default_system_prompt})

            while True:
                # Get user input
                user_input = console.input("You: ")

                self.full_conversation_history.append({"role": "user", "content": user_input})

                if user_input == "/quit":
                    console.print("Goodbye!", style="bold green")
                    break

                elif user_input == "/help":
                    console.print("Available commands:", style="bold cyan")
                    console.print("/help - Show list of available commands")
                    console.print("/quit - Quit the chat session")
                    console.print("/reset - Reset the conversation history")
                    console.print("/save - Save the conversation history to a file")
                    continue

                elif user_input == "/reset":
                    self.default_conversation_history = [{"role": "system", "content": default_system_prompt}]
                    self.user_conversation_history = [{"role": "system", "content": system_input if system_input else default_system_prompt}]
                    console.print("Conversation history reset!", style="bold green")
                    self.full_conversation_history = []
                    continue

                elif user_input == "/save":
                    with open("conversation_history.json", "w") as f:
                        json.dump(self.full_conversation_history, f, indent=4)
                    console.print("Conversation history saved to conversation_history.json!", style="bold green")
                    continue

                # Create a new list for the default system prompt
                new_default_conversation_history = [{"role": "system", "content": default_system_prompt}, {"role": "user", "content": user_input}]

                console.print("Processing default response...", style="bold cyan", end='')

                start_time = time.time()

                # Send the entire conversation history to the OpenRouter API for the default system prompt
                async def get_default_response():
                    try:
                        response_default = await self.get_api_response(session, {"model": model, "messages": new_default_conversation_history})
                    except Exception as e:
                        console.print("\n")
                        console.print(f"Error: {str(e)}", style="error")
                        self.default_conversation_history.append({"role": "assistant", "content": f"Error: {str(e)}"})
                        self.full_conversation_history.append({"role": "assistant", "content": f"Error: {str(e)}"})
                    return response_default

                # Create a new list for the user-entered system prompt
                new_user_conversation_history = [{"role": "system", "content": system_input if system_input else default_system_prompt}, {"role": "user", "content": user_input}]

                console.print("Processing user response...", style="bold cyan", end='')

                start_time = time.time()

                # Send the entire conversation history to the OpenRouter API for the user-entered system prompt
                async def get_user_response():
                    try:
                        response_user = await self.get_api_response(session, {"model": model, "messages": new_user_conversation_history})
                    except Exception as e:
                        console.print("\n")
                        console.print(f"Error: {str(e)}", style="error")
                        self.user_conversation_history.append({"role": "assistant", "content": f"Error: {str(e)}"})
                        self.full_conversation_history.append({"role": "assistant", "content": f"Error: {str(e)}"})
                    return response_user

                tasks = asyncio.gather(get_default_response(), get_user_response())
                responses = await tasks

                default_response = responses[0]
                user_response = responses[1]

                end_time = time.time()

                console.print("\n")

                if "choices" in default_response:
                    if default_response["choices"][0]["message"]["content"].strip():
                        # Extract the content value from the response
                        content = default_response["choices"][0]["message"]["content"]

                        # Create a RichText object for the AI's response
                        text = Text(content)

                        # Create a Rich panel for the AI's response
                        panel = Panel(text, title="[border]Default AI Response[/border]", border_style="border")

                        # Print the AI's response to the console
                        console.print(panel)

                        # Update the conversation history with the AI's response
                        self.default_conversation_history.append({"role": "assistant", "content": content})
                        self.full_conversation_history.append({"role": "assistant", "content": content})
                    else:
                        console.print("Error: Invalid response from OpenRouter API", style="error")
                        self.default_conversation_history.append({"role": "assistant", "content": "Error: Invalid response from OpenRouter API"})
                        self.full_conversation_history.append({"role": "assistant", "content": "Error: Invalid response from OpenRouter API"})
                else:
                    console.print("Error: Invalid response from OpenRouter API", style="error")
                    self.default_conversation_history.append({"role": "assistant", "content": "Error: Invalid response from OpenRouter API"})
                    self.full_conversation_history.append({"role": "assistant", "content": "Error: Invalid response from OpenRouter API"})

                console.print(f"Default response generated in {end_time - start_time} seconds", style="bold green")

                if "choices" in user_response:
                    if user_response["choices"][0]["message"]["content"].strip():
                        # Extract the content value from the response
                        content = user_response["choices"][0]["message"]["content"]

                        # Create a RichText object for the AI's response
                        text = Text(content)

                        # Create a Rich panel for the AI's response
                        panel = Panel(text, title="[border]User AI Response[/border]", border_style="border")

                        # Print the AI's response to the console
                        console.print(panel)

                        # Update the conversation history with the AI's response
                        self.user_conversation_history.append({"role": "assistant", "content": content})
                        self.full_conversation_history.append({"role": "assistant", "content": content})
                    else:
                        console.print("Error: Invalid response from OpenRouter API", style="error")
                        self.user_conversation_history.append({"role": "assistant", "content": "Error: Invalid response from OpenRouter API"})
                        self.full_conversation_history.append({"role": "assistant", "content": "Error: Invalid response from OpenRouter API"})
                else:
                    console.print("Error: Invalid response from OpenRouter API", style="error")
                    self.user_conversation_history.append({"role": "assistant", "content": "Error: Invalid response from OpenRouter API"})
                    self.full_conversation_history.append({"role": "assistant", "content": "Error: Invalid response from OpenRouter API"})

                console.print(f"User response generated in {end_time - start_time} seconds", style="bold green")

async def main():
    session = ChatSession()
    await session.main()

asyncio.run(main())
