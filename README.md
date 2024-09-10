# OpenRouter Prompt Companion

A Python shell prompt Companion that uses the OpenRouter API to generate responses to user queries.

## Features

* Uses the OpenRouter API to generate responses to user queries
* Allows users to enter a custom system prompt
* Allows users to save conversation history to a file
* Includes a `/help` command to display available commands
* Includes a `/reset` command to reset conversation history
* Includes a `/save` command to save conversation history to a file
* Includes a `/quit` command to quit the script

## Installation

### Step 1: Clone the repository
```bash
git clone https://github.com/dheeraj21/open-router-prompt-companion.git
```
### Step 2: Install the required libraries
```bash
cd open-router-prompt-companion
pip install -r requirements.txt
```
### Step 3: Set the OpenRouter API key
```bash
rename .env.example file to .env and add your open router api key
```
### Step 4: Run the prompt companion
```bash
python main.py
```

## Usage

1. Run the script: `python main.py`
2. Enter a system prompt (optional): `Enter a system prompt (optional):`
3. Enter user input: `You:`
4. View the generated responses: `AI (Default System Prompt):` and `AI (User-Entered System Prompt):`

## Set OPENROUTER API KEY

rename .env.example file to .env and add your open router api key


## License

This project is licensed under the APACHE 2.0.


