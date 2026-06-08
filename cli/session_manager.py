import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from utils.logger import logger


class SessionManager:
    """Manages session persistence and restoration."""
    
    def __init__(self, session_dir: str = "~/.mimi/sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session state
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.loaded_session_id: Optional[str] = None
        self.session_loaded_from_file: bool = False
        
        # Session data
        self.conversation: List = []
        self.tool_usage_history: List = []
        self.thread_id: Optional[str] = None

    def _serialize_message(self, message) -> Dict[str, Any]:
        """Serialize a message for storage."""
        if isinstance(message, HumanMessage):
            return {"type": "human", "content": message.content}
        elif isinstance(message, AIMessage):
            return {"type": "ai", "content": message.content}
        elif isinstance(message, ToolMessage):
            return {
                "type": "tool", 
                "name": getattr(message, 'name', 'unknown'), 
                "content": message.content
            }
        else:
            return {"type": "unknown", "content": str(message)}

    def _deserialize_message(self, msg_data: Dict[str, Any]):
        """Deserialize a message from storage."""
        msg_type = msg_data.get("type")
        content = msg_data.get("content", "")
        
        if msg_type == "human":
            return HumanMessage(content=content)
        elif msg_type == "ai":
            return AIMessage(content=content)
        elif msg_type == "tool":
            return ToolMessage(
                content=content,
                name=msg_data.get("name", "unknown")
            )
        else:
            return None

    def save_session(self, thread_id: str) -> bool:
        """Save current session data to file."""
        session_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "thread_id": thread_id,
            "conversation": [self._serialize_message(msg) for msg in self.conversation],
            "tool_usage": self.tool_usage_history
        }
        
        session_file = self.session_dir / f"{self.session_id}.json"
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Session saved to {session_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available session files with metadata."""
        sessions = []
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    session_id = session_file.stem
                    session_info = {
                        "session_id": session_id,
                        "filename": session_file.name,
                        "timestamp": data.get("timestamp", "Unknown"),
                        "thread_id": data.get("thread_id", "None"),
                        "conversation_count": len(data.get("conversation", [])),
                        "tool_usage_count": len(data.get("tool_usage", [])),
                        "size_bytes": session_file.stat().st_size
                    }
                    sessions.append(session_info)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error reading session file {session_file.name}: {e}")
                    sessions.append({
                        "session_id": session_file.stem,
                        "filename": session_file.name,
                        "timestamp": "Invalid format",
                        "thread_id": "None",
                        "conversation_count": 0,
                        "tool_usage_count": 0,
                        "size_bytes": session_file.stat().st_size,
                        "error": str(e)
                    })
            
            # Sort by timestamp (newest first)
            sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return sessions
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []

    def load_session(self, session_id: str) -> Tuple[bool, str]:
        """Load a session from file and restore conversation/tool usage history."""
        session_file = self.session_dir / f"{session_id}.json"
        
        if not session_file.exists():
            logger.error(f"Session file not found: {session_file}")
            return False, f"Session '{session_id}' not found"
        
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate session data structure
            if "conversation" not in data or "tool_usage" not in data:
                logger.error(f"Invalid session format in {session_id}")
                return False, f"Invalid session format in '{session_id}'"
            
            # Clear current session data
            self.conversation = []
            self.tool_usage_history = []
            
            # Restore conversation messages
            for msg_data in data.get("conversation", []):
                msg = self._deserialize_message(msg_data)
                if msg:
                    self.conversation.append(msg)
            
            # Restore tool usage history
            self.tool_usage_history = data.get("tool_usage", [])
            
            # Restore thread_id if present
            saved_thread_id = data.get("thread_id")
            if saved_thread_id:
                self.thread_id = saved_thread_id
                logger.info(f"Restored thread_id: {saved_thread_id}")
            
            # Update session tracking
            self.loaded_session_id = session_id
            self.session_loaded_from_file = True
            self.session_id = session_id
            
            logger.info(f"Loaded session '{session_id}' with {len(self.conversation)} messages")
            return True, f"Session '{session_id}' loaded successfully with {len(self.conversation)} messages"
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return False, f"Error loading session '{session_id}': {str(e)}"

    def switch_session(self, session_id: str, current_thread_id: str) -> Tuple[bool, str]:
        """Switch to a different session (saves current, loads new)."""
        # Save current session first
        if len(self.conversation) > 0 or len(self.tool_usage_history) > 0:
            self.save_session(current_thread_id)
        
        # Load new session
        success, message = self.load_session(session_id)
        return success, message

    def delete_session(self, session_id: str) -> Tuple[bool, str]:
        """Delete a session file."""
        session_file = self.session_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return False, f"Session '{session_id}' not found"
        
        try:
            # Prevent deleting currently loaded session
            if self.loaded_session_id == session_id or self.session_id == session_id:
                return False, f"Cannot delete currently active session '{session_id}'"
            
            session_file.unlink()
            logger.info(f"Deleted session file: {session_file}")
            return True, f"Session '{session_id}' deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False, f"Error deleting session '{session_id}': {str(e)}"

    def get_session_info(self) -> Dict[str, Any]:
        """Get detailed information about current session."""
        return {
            "Current Session ID": self.session_id,
            "Loaded From File": "Yes" if self.session_loaded_from_file else "No",
            "Loaded Session ID": self.loaded_session_id if self.loaded_session_id else "None",
            "Conversation Messages": len(self.conversation),
            "Tool Usage Records": len(self.tool_usage_history),
            "Thread ID": self.thread_id,
            "Session Directory": str(self.session_dir.resolve())
        }

    def track_tool_usage(self, tool_name: str, input_data: Any, output: Any, success: bool):
        """Track tool usage for analytics."""
        self.tool_usage_history.append({
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "input": input_data,
            "output": output,
            "success": success
        })
        logger.info(f"Tool used: {tool_name} - Success: {success}")