import os
from pydantic import BaseModel, Field


class FileSearchArgs(BaseModel):
    directory: str = Field(description="The directory path to explore, e.g., 'C:/Users/rajes/Documents'.")
    extension: str = Field(description="Filter by file extension, e.g., '.txt', '.pdf', '.png'. Leave empty for all.")


def explore_directory(directory: str, extension: str = "") -> str:
    """Explores files within a given directory directory path, filtered optionally by extension."""
    if not os.path.exists(directory):
        return f"Directory path '{directory}' cannot be resolved or found, sir."

    try:
        files = os.listdir(directory)
        if extension:
            files = [f for f in files if f.endswith(extension)]

        file_list = "\n- ".join(files[:20])  # Limit to top 20 lines for clean parsing
        return f"Contents of {directory}:\n- {file_list if file_list else 'No matching files found.'}"
    except Exception as e:
        return f"File access verification error: {str(e)}"