from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
from config.config import get_expanded_path


def setup_check_pointer(sqlite_db_path: str = None) -> SqliteSaver:
    """
    Setup SQLite checkpointer with path from config or default.
    
    Args:
        sqlite_db_path: Optional explicit path. If None, uses config value.
    
    Returns:
        SqliteSaver instance
    """
    if sqlite_db_path is None:
        sqlite_db_path = get_expanded_path("sqlite_db", "~/.mimi/database/checkpointer.db")
    
    # Ensure parent directory exists
    db_dir = os.path.dirname(sqlite_db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(sqlite_db_path, check_same_thread=False)
    checkPointer = SqliteSaver(
        conn, serde=JsonPlusSerializer(allowed_json_modules="messages")
    )
    checkPointer.setup()
    return checkPointer