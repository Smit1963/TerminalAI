import os
import subprocess
import re
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.align import Align
from rich.box import ROUNDED

console = Console()
TERMINAL_BUFFER = []
MAX_BUFFER_LINES = 40
ERROR_PATTERNS = [
    re.compile(r"error", re.IGNORECASE),
    re.compile(r"exception", re.IGNORECASE),
    re.compile(r"failed", re.IGNORECASE),
    re.compile(r"fatal", re.IGNORECASE),
    re.compile(r"traceback", re.IGNORECASE),
    re.compile(r"stack trace", re.IGNORECASE),
]

KNOWN_COMMANDS = [
    'ls', 'dir', 'cd', 'pwd', 'echo', 'cat', 'type', 'python', 'pip', 'npm', 'node', 'git', 'rm', 'del',
    'copy', 'move', 'mv', 'cp', 'touch', 'mkdir', 'rmdir', 'cls', 'clear', 'exit', 'whoami', 'find', 'grep',
    'set', 'export', 'env', 'where', 'which', 'start', 'code', 'run', 'java', 'javac', 'curl', 'wget', 'ssh',
    'scp', 'ping', 'tracert', 'ipconfig', 'ifconfig', 'tasklist', 'taskkill', 'kill', 'ps', 'top', 'htop',
    'sudo', 'choco', 'apt', 'yum', 'brew', 'docker', 'kubectl', 'conda', 'poetry', 'venv', 'virtualenv',
]
COMMAND_PATTERN = re.compile(rf"^({'|'.join(KNOWN_COMMANDS)})($|\s)", re.IGNORECASE)

def detect_error(output: str) -> bool:
    return any(p.search(output) for p in ERROR_PATTERNS)

def add_to_buffer(text: str):
    global TERMINAL_BUFFER
    lines = text.splitlines()
    TERMINAL_BUFFER.extend(lines)
    if len(TERMINAL_BUFFER) > MAX_BUFFER_LINES:
        TERMINAL_BUFFER = TERMINAL_BUFFER[-MAX_BUFFER_LINES:]

def get_groq_api_key():
    return os.environ.get("GROQ_API_KEY")

def ask_groq(prompt: str, context: str = "") -> str:
    api_key = get_groq_api_key()
    if not api_key:
        return "[red]❌ GROQ_API_KEY not set. Please set your Groq API key in your environment.[/red]"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-r1-distill-llama-70b",
        "messages": [
            {"role": "system", "content": "You are a fun, witty, and highly intelligent terminal copilot. You help debug errors, explain commands, and provide actionable, creative, and concise solutions. You can also chat like ChatGPT or Gemini. Be friendly and engaging!"},
            {"role": "user", "content": f"{prompt}\n\nRecent terminal output:\n{context}"}
        ],
        "temperature": 0.5,
        "max_tokens": 600
    }
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[red]❌ Error calling Groq API: {e}[/red]"

def run_shell_command(cmd: str):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        add_to_buffer(output)
        return output, result.returncode
    except Exception as e:
        return str(e), 1

def is_question(user_input: str) -> bool:
    user_input = user_input.strip()
    if user_input.startswith('?') or user_input.lower().startswith('ai '):
        return True
    if user_input.endswith('?'):
        return True
    if COMMAND_PATTERN.match(user_input):
        return False
    if re.match(r"^[./\\]|^[a-zA-Z0-9_]+=", user_input):
        return False
    if re.search(r"[a-zA-Z]", user_input) and ' ' in user_input:
        return True
    return False

def strip_think_sections(text: str) -> str:
    # Remove <think>...</think> blocks, including the tags
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def markdown_to_chat(text: str) -> str:
    import re
    # Remove ```lang and ```
    text = re.sub(r"```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"```", "", text)
    # Optionally, indent code lines for clarity
    lines = text.splitlines()
    new_lines = []
    in_code = False
    for line in lines:
        # Simple heuristic: indent lines that look like code
        if line.strip().startswith(("pip ", "python ", "import ", "print(", "conda ", "# ", "def ", "class ", "for ", "if ", "while ", "    ")):
            new_lines.append(f"    {line}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines).strip()

def print_chatbot_response(message: str):
    formatted = f"[bold cyan]🤖 AI:[/bold cyan]\n\n{message}"
    panel = Panel(
        Align.left(formatted),
        title="",
        border_style="magenta",
        box=ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)

def main():
    console.print(Panel("[bold cyan]Terminal AI Copilot[/bold cyan]\nType a shell command or ask a question.\nPrefix with '?' or 'ai' to ask the AI. Type 'exit' to quit.", title="Terminal Copilot"))
    if not get_groq_api_key():
        console.print("[yellow]⚠️  Set your GROQ_API_KEY environment variable to enable AI features.[/yellow]")
    while True:
        user_input = Prompt.ask("[bold green]$[/bold green]", default="")
        if user_input.strip().lower() in ("exit", "quit"): 
            break
        if not user_input.strip():
            continue
        if is_question(user_input):
            # Remove prefix if present
            if user_input.startswith('?'):
                user_input = user_input[1:].strip()
            if user_input.lower().startswith('ai '):
                user_input = user_input[3:].strip()
            context = "\n".join(TERMINAL_BUFFER[-20:])
            answer = ask_groq(user_input, context)
            print_chatbot_response(markdown_to_chat(strip_think_sections(answer)))
        else:
            output, code = run_shell_command(user_input)
            console.print(Panel(output, title=f"[bold]Command Output (exit code {code})[/bold]", style="cyan"))
            if detect_error(output):
                explain = Prompt.ask("[red]❗ Error detected. Explain this error?[/red] (y/n)", default="y")
                if explain.lower().startswith("y"):
                    context = "\n".join(TERMINAL_BUFFER[-20:])
                    answer = ask_groq(f"Explain and suggest a fix for this error:", context)
                    print_chatbot_response(markdown_to_chat(strip_think_sections(answer)))

if __name__ == "__main__":
    main() 