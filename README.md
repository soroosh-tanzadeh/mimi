# Mimi: Your Kawaii Coding Assistant

<center>
    <figure>
        <img src="./.assets/logo.png" height="250" width="250"
            alt="Mimi">
    </figure>
</center>

## How to start development

```bash
# Clone the repository
git clone <repository-url>
cd mimi

# Install dependencies
pip install -r requirements.txt
```

## Configuration

MiMi can be configured using:
1. Environment variables (`.env` file)
2. YAML configuration file (`config.yaml`)
3. JSON configuration file (`config.json`)

### Example .env file:
```bash
MODEL="qwen/qwen3-coder"
INSTRUCTION="system-prompts/code-assistant-prompt-planner.md"
OPENAI_API_KEY="your-api-key-here"
OPENAI_API_BASE_URL="BASEURL_HERE"
```

### Example config.yaml file:
```yaml
model:
  name: "qwen/qwen3-coder"
  api_key: "your-api-key-here"
  base_url: "BASE_URL_HERE"

agent:
  instruction: "system-prompts/code-assistant-prompt-planner.md"
  session_dir: "sessions"
  log_level: "INFO"
  log_file: "logs/mimi.log"
  prompt: "User> "
```

## Usage

```bash
# Run the agent
python main.py

# Run tests
python tests/run_tests.py
```

## Features

- **Persistent Sessions**: Conversations are saved and can be resumed
- **Tool Tracking**: All tool usage is logged for analysis
- **Enhanced Logging**: Detailed logs for debugging and monitoring
- **Configuration Flexibility**: Multiple ways to configure the agent
- **Robust Error Handling**: Graceful handling of errors and exceptions
- **Comprehensive Testing**: Thorough test coverage for reliability

## Directory Structure

```
mimi/
├── cli/                 # Command line interface components
├── config/              # Configuration management
├── logs/                # Log files
├── sessions/            # Session data
├── system-prompts/      # System prompt templates
├── tests/               # Test suite
├── tools/               # Tool implementations
├── utils/               # Utility functions
├── main.py             # Entry point
├── config.yaml         # Default configuration
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Testing

Run the test suite with:

```bash
python tests/run_tests.py
```

The test suite includes:
- Configuration manager tests
- Agent functionality tests
- File tool tests
- Integration tests

## Logging

Logs are saved to `logs/mimi.log` by default. The log level can be configured in the configuration file.

## Sessions

Conversation sessions are automatically saved to the `sessions/` directory with timestamps. Each session includes:
- Complete conversation history
- Tool usage records
- Session metadata