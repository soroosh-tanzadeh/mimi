from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


def setup_check_pointer(sqliteDb) -> SqliteSaver:
    conn = sqlite3.connect(sqliteDb, check_same_thread=False)
    checkPointer = SqliteSaver(
        conn, serde=JsonPlusSerializer(allowed_json_modules="messages")
    )  # type: SqliteSaver
    checkPointer.setup()
    return checkPointer
