# Mimi: Your Kawaii Coding Assistant

<center>
    <figure>
        <img src="./.assets/logo.png" height="250" width="250"
            alt="Mimi">
    </figure>
</center>

Meet **Mimi**, your adorable and intelligent coding companion! Mimi is an AI-powered code assistant designed to help you with programming tasks.

## Requirements

- Python 3.x
- Conda (recommended)
- python-dotenv (installed via environment)

Install dependencies using:

```bash
# Recommended: create the conda env and activate it
conda env create -f environment.yml
conda activate langchain

# Alternative (pip-only):
# pip install -r requirements.txt
```

## Configuration

Create a `.env` file based on the provided example. The following environment variables are required:

- `OPENAI_API_KEY`: Your OpenAI API key.
- `OPENAI_API_BASE_URL`: Base URL for the OpenAI API endpoint.
- `MODEL`: The model to use (default: gpt-3.5-turbo).
- `INSTRUCTION`: Path to the system prompt file (default: system-prompts/code-assistant-prompt-planner.md) OR an inline instruction string.

## Usage

Run Mimi using:

```bash
conda activate langchain
python main.py
```

Once started, you can interact with Mimi via a chat interface. Type `quit` or `exit` to say goodbye!

## Model

Mimi uses the **Qwen3-Coder-480b-A35B-Instruct** model hosted via Arvan Cloud AI Gateway by default.

## License

This project is licensed under the MIT License.
