import json
import os
from langchain.tools import tool


@tool
def read_file(filename: str) -> str:
    """
    Read the content of a file
    """
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {filename}: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """
    List files in a directory
    """
    try:
        files = os.listdir(directory)
        return json.dumps(
            {"directory": directory, "files": files, "success": True, "error": None}
        )
    except Exception as e:
        return json.dumps(
            {"directory": directory, "files": [], "success": False, "error": str(e)}
        )


@tool
def write_to_file(filename: str, content: str, overwrite: bool = False) -> str:
    """
    Write content to a file
    """
    if ".." in filename or filename.startswith("/"):
        return json.dumps(
            {
                "filename": filename,
                "success": False,
                "error": "Forbidden, you can create files only in the current directory.",
            }
        )

    # Create parent directory if needed
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    except OSError:
        pass

    # Overwrite if needed
    if overwrite and os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError:
            pass

    try:
        with open(filename, "w") as f:
            f.write(content)
        return json.dumps({"filename": filename, "success": True, "error": None})
    except Exception as e:
        return json.dumps({"filename": filename, "success": False, "error": str(e)})
