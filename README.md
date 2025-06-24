# TerminalAI

TerminalAI is an intelligent terminal copilot that enhances your command-line experience with AI-powered assistance. It can execute shell commands, answer questions, explain errors, and provide actionable solutions—all from your terminal. Powered by the Groq API and featuring a friendly, engaging AI assistant, TerminalAI helps you debug, learn, and work more efficiently.

## Features
- Run shell commands and view output in a rich, styled interface
- Ask questions or for explanations by prefixing with `?` or `ai`
- Automatic error detection and AI-powered explanations/suggestions
- Maintains a buffer of recent terminal output for context-aware answers
- Supports both Windows and Unix-like commands

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd TerminalAI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Groq API key:**
   - Obtain a Groq API key from [Groq](https://groq.com/).
   - Set the environment variable in your shell:
     - **Linux/macOS:**
       ```bash
       export GROQ_API_KEY=your_api_key_here
       ```
     - **Windows (PowerShell):**
       ```powershell
       $env:GROQ_API_KEY="your_api_key_here"
       ```

## Usage

Run the main script:
```bash
python terminal_ai.py
```

- **To run a shell command:**
  Just type the command as you would in your terminal (e.g., `ls`, `dir`, `python script.py`).

- **To ask the AI a question:**
  Prefix your input with `?` or `ai`, or simply type a natural language question (e.g., `? How do I use git rebase?`).

- **Error detection:**
  If a command fails, TerminalAI will offer to explain the error and suggest a fix using the AI.

- **Exit:**
  Type `exit` or `quit` to leave the program.

## Example
```
$ ls
$ python script.py
$ ? What does the error "ModuleNotFoundError" mean?
$ ai Suggest a way to optimize this bash script
```

## Requirements
- Python 3.7+
- [rich](https://github.com/Textualize/rich)
- [requests](https://docs.python-requests.org/)

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## License
MIT License 