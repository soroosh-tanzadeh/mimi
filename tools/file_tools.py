import json
import os
import re
from pathlib import Path
from langchain.tools import tool


def _validate_file_path(filename: str, allowed_directories=None) -> tuple[bool, str]:
    """
    Validate file path for security.
    
    Args:
        filename: Path to validate
        allowed_directories: List of allowed base directories
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if allowed_directories is None:
        allowed_directories = [".", "projects", "workspace"]
    
    # Convert to absolute path for validation
    try:
        abs_path = os.path.abspath(filename)
    except Exception as e:
        return False, f"Invalid path: {str(e)}"
    
    # Check for directory traversal attempts
    if ".." in Path(filename).parts:
        return False, "Directory traversal (..) is not allowed"
    
    # Check for symlinks (potential security risk)
    if os.path.islink(filename):
        return False, "Symbolic links are not allowed"
    
    # Check if path is within allowed directories
    is_allowed = False
    for allowed_dir in allowed_directories:
        allowed_abs = os.path.abspath(allowed_dir)
        try:
            # Check if the resolved path is within the allowed directory
            if os.path.commonpath([abs_path, allowed_abs]) == allowed_abs:
                is_allowed = True
                break
        except ValueError:
            # Paths don't share a common prefix
            continue
    
    if not is_allowed:
        return False, f"Path must be within allowed directories: {allowed_directories}"
    
    return True, ""


def _check_file_size(filename: str, max_size_mb: int = 10) -> tuple[bool, str]:
    """
    Check if file size is within limits.
    
    Args:
        filename: File to check
        max_size_mb: Maximum size in MB
        
    Returns:
        Tuple of (is_within_limit, error_message)
    """
    try:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            max_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_bytes:
                return False, f"File size ({file_size / (1024*1024):.1f}MB) exceeds limit of {max_size_mb}MB"
    except Exception:
        # If we can't check size, proceed with caution
        pass
    
    return True, ""


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
    # Validate path
    is_valid, error_msg = _validate_file_path(filename)
    if not is_valid:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"Security validation failed: {error_msg}",
            "content": None
        })
    
    # Check file size
    is_within_limit, size_error = _check_file_size(filename)
    if not is_within_limit:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"File size limit exceeded: {size_error}",
            "content": None
        })
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        return json.dumps({
            "filename": filename,
            "success": True,
            "error": None,
            "content": content,
            "size_bytes": len(content.encode('utf-8'))
        })
    except Exception as e:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"Error reading file: {str(e)}",
            "content": None
        })


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
    # Validate path
    is_valid, error_msg = _validate_file_path(directory)
    if not is_valid:
        return json.dumps(
            {"directory": directory, "files": [], "success": False, "error": f"Security validation failed: {error_msg}"}
        )
    
    try:
        files = os.listdir(directory)
        # Sort files for better readability
        files.sort()
        
        # Add file type indicators
        file_details = []
        for file in files:
            file_path = os.path.join(directory, file)
            try:
                if os.path.isdir(file_path):
                    file_type = "directory"
                elif os.path.isfile(file_path):
                    file_type = "file"
                elif os.path.islink(file_path):
                    file_type = "link"
                else:
                    file_type = "other"
                
                file_details.append({
                    "name": file,
                    "type": file_type,
                    "size": os.path.getsize(file_path) if file_type == "file" else None
                })
            except Exception:
                file_details.append({"name": file, "type": "unknown", "size": None})
        
        return json.dumps({
            "directory": directory,
            "files": files,
            "file_details": file_details,
            "success": True,
            "error": None
        })
    except Exception as e:
        return json.dumps({
            "directory": directory,
            "files": [],
            "file_details": [],
            "success": False,
            "error": str(e)
        })


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
    # Validate path
    is_valid, error_msg = _validate_file_path(filename)
    if not is_valid:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"Security validation failed: {error_msg}"
        })
    
    # Check if file exists and overwrite is False
    if os.path.exists(filename) and not overwrite:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": "File already exists and overwrite is False"
        })
    
    # Check content size
    content_size = len(file_content.encode('utf-8'))
    max_size_mb = 10  # 10MB limit
    max_bytes = max_size_mb * 1024 * 1024
    
    if content_size > max_bytes:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"Content size ({content_size / (1024*1024):.1f}MB) exceeds limit of {max_size_mb}MB"
        })
    
    # Create parent directory if needed
    try:
        parent_dir = os.path.dirname(filename)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
    except OSError as e:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"Failed to create parent directory: {str(e)}"
        })
    
    # Write the file
    try:
        mode = "w" if overwrite else "x"  # Use exclusive creation if not overwriting
        with open(filename, mode, encoding="utf-8") as f:
            f.write(file_content)
        
        # Verify the file was written
        if os.path.exists(filename):
            actual_size = os.path.getsize(filename)
            return json.dumps({
                "filename": filename,
                "success": True,
                "error": None,
                "size_bytes": actual_size,
                "overwritten": overwrite and os.path.exists(filename)  # Check if file existed before
            })
        else:
            return json.dumps({
                "filename": filename,
                "success": False,
                "error": "File was not created"
            })
    except FileExistsError:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": "File already exists (use overwrite=True to replace)"
        })
    except Exception as e:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"Error writing file: {str(e)}"
        })


@tool(description="Check file information and permissions")
def file_info(filename: str) -> str:
    """
    Get information about a file or directory.
    
    Args:
        filename (str): The name or path of the file to inspect.
        
    Returns:
        str: JSON string with file information.
    """
    # Validate path
    is_valid, error_msg = _validate_file_path(filename)
    if not is_valid:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"Security validation failed: {error_msg}"
        })
    
    try:
        stat_info = os.stat(filename)
        
        info = {
            "filename": filename,
            "success": True,
            "error": None,
            "exists": os.path.exists(filename),
            "is_file": os.path.isfile(filename),
            "is_dir": os.path.isdir(filename),
            "is_link": os.path.islink(filename),
            "size_bytes": stat_info.st_size if os.path.isfile(filename) else None,
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "accessed": stat_info.st_atime,
            "permissions": oct(stat_info.st_mode)[-3:],
            "readable": os.access(filename, os.R_OK),
            "writable": os.access(filename, os.W_OK),
            "executable": os.access(filename, os.X_OK)
        }
        
        return json.dumps(info)
    except FileNotFoundError:
        return json.dumps({
            "filename": filename,
            "success": True,
            "error": None,
            "exists": False,
            "message": "File does not exist"
        })
    except Exception as e:
        return json.dumps({
            "filename": filename,
            "success": False,
            "error": f"Error getting file info: {str(e)}"
        })