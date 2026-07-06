import os
import subprocess
from pathlib import Path
from pydantic import BaseModel, Field

# Ensure a dedicated macros folder exists inside your project
SKILLS_DIR = Path(__file__).resolve().parent.parent / "data" / "custom_skills"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)


class SaveSkillArgs(BaseModel):
    skill_name: str = Field(description="The unique, lowercase snake_case name of the skill (e.g., 'clean_workspace').")
    script_content: str = Field(
        description="The raw, executable Windows Batch or PowerShell commands that perform the skill.")


class RunSkillArgs(BaseModel):
    skill_name: str = Field(description="The unique name of the custom skill script to execute.")


def save_custom_skill(skill_name: str, script_content: str) -> str:
    """Saves a dynamically generated text script into the local machine's skill directory library."""
    # Sanitize name to ensure it saves cleanly as a Windows Batch file
    safe_name = "".join(c for c in skill_name.lower().replace(" ", "_") if c.isalnum() or c == "_")
    file_path = SKILLS_DIR / f"{safe_name}.bat"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    return f"Skill '{skill_name}' has been compiled and saved to my physical sub-routines, sir."


def execute_custom_skill(skill_name: str) -> str:
    """Locates and runs a previously saved custom batch skill script completely in the background."""
    safe_name = "".join(c for c in skill_name.lower().replace(" ", "_") if c.isalnum() or c == "_")
    file_path = SKILLS_DIR / f"{safe_name}.bat"

    if not file_path.exists():
        return f"I am sorry sir, I have no operational record of a skill named '{skill_name}'."

    try:
        # Run the compiled batch file seamlessly in the background
        result = subprocess.run(
            str(file_path),
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        return f"Skill '{skill_name}' executed successfully, sir.\nLogs:\n{output if output else 'Process cleared with exit code 0.'}"
    except subprocess.CalledProcessError as e:
        return f"Skill execution halted due to error:\n{e.stderr}"