import os


def run_terminal_command(command: str) -> str:
    """Runs an arbitrary command in the Windows Command Prompt (cmd) and returns the output."""
    try:
        stream = os.popen(command)
        output = stream.read()
        return f"Command executed. Output:\n{output[:1000]}"
    except Exception as e:
        return f"Failed to execute command: {str(e)}"