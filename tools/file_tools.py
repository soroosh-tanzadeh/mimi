import json
import os
from langchain.tools import tool


@tool(description="Read the content of a file.")
def read_file(filename: str) -> str:
    """
    Read the content of a file.

    This tool allows the agent to read the content of a specified file.
    The agent should provide the filename or path of the file it wants to read.

    Args:
        filename (str): The name or path of the file to read. Can be a relative path from the current directory.

    Returns:
        str: Contains either the file content as a string, or an error message if the file cannot be read.
             The agent should check if the response contains an error message by looking for patterns like "Error:"
    """
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {filename}: {str(e)}"


@tool(description="List files in a directory.")
def list_files(directory: str = ".") -> str:
    """
    List files in a directory.

    This tool provides the agent with a list of files in a specified directory.
    The agent can use this to explore the file structure and locate files of interest.

    Args:
        directory (str, optional): The directory path to list files from. Defaults to "." (current directory).
                                   The agent can specify a subdirectory path like "src" or "tests".

    Returns:
        str: A JSON string with the following structure:
             {
                 "directory": string,     # The directory that was listed
                 "files": [string],       # Array of filenames in the directory
                 "success": boolean,      # Whether the operation was successful
                 "error": string or null  # Error message if operation failed
             }
             The agent should parse this JSON response to extract the list of files.
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


@tool(description="Write content to a file")
def write_to_file(filename: str, file_content: str, overwrite: bool = False) -> str:
    """
    Write content to a file.

    This tool allows the agent to create or update files with specified content.
    The agent should provide the filename, content, and whether to overwrite existing files.

    Args:
        filename (str): The name or path of the file to write to.
                        Should be a relative path from the current directory.
                        Parent directories will be created automatically if needed.
        file_content (str): The complete content to write to the file.
                            The agent should ensure this contains the full intended content.
        overwrite (bool, optional): Whether to overwrite the file if it already exists. Defaults to False.
                                    If False, the tool will not modify existing files.
                                    If True, the tool will replace the existing file content.

    Returns:
        str: A JSON string with the following structure:
             {
                 "filename": string,      # The file that was written to
                 "success": boolean,      # Whether the operation was successful
                 "error": string or null  # Error message if operation failed
             }
             The agent should check the success field to confirm the operation worked.
    """
    # Security check: Prevent absolute paths and parent directory traversal
    if os.path.isabs(filename) or ".." in os.path.normpath(filename).split(os.sep):
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
            f.write(file_content)
        return json.dumps({"filename": filename, "success": True, "error": None})
    except Exception as e:
        return json.dumps({"filename": filename, "success": False, "error": str(e)})
