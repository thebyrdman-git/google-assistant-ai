"""
Conversation State Management
Maintains conversation history across user sessions
"""

import logging
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation state and history"""
    
    def __init__(self, max_history: int = 10, session_timeout_minutes: int = 30):
        """
        Initialize conversation manager
        
        Args:
            max_history: Maximum number of messages to keep in history
            session_timeout_minutes: Minutes before session expires
        """
        self.max_history = max_history
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        
        # Store conversation history: {session_id: [messages]}
        self.conversations: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        
        # Track last access time: {session_id: datetime}
        self.last_access: Dict[str, datetime] = {}
        
        logger.info(
            f"Initialized ConversationManager "
            f"(max_history={max_history}, timeout={session_timeout_minutes}min)"
        )
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of conversation messages
        """
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        # Update last access time
        self.last_access[session_id] = datetime.now()
        
        # Return conversation history (or empty list for new sessions)
        history = self.conversations.get(session_id, [])
        
        logger.debug(f"Retrieved history for session {session_id}: {len(history)} messages")
        return history.copy()
    
    def update_history(
        self,
        session_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """
        Update conversation history for a session
        
        Args:
            session_id: Unique session identifier
            messages: Updated list of conversation messages
        """
        # Enforce maximum history length
        if len(messages) > self.max_history:
            # Keep system prompt (if exists) + recent messages
            if messages and messages[0].get('role') == 'system':
                messages = [messages[0]] + messages[-(self.max_history-1):]
            else:
                messages = messages[-self.max_history:]
        
        # Update conversation
        self.conversations[session_id] = messages
        self.last_access[session_id] = datetime.now()
        
        logger.debug(
            f"Updated history for session {session_id}: {len(messages)} messages"
        )
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear conversation history for a session
        
        Args:
            session_id: Session to clear
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
        if session_id in self.last_access:
            del self.last_access[session_id]
        
        logger.info(f"Cleared session {session_id}")
    
    def _cleanup_expired_sessions(self) -> None:
        """Remove sessions that have expired"""
        now = datetime.now()
        expired_sessions = [
            session_id
            for session_id, last_access in self.last_access.items()
            if now - last_access > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            self.clear_session(session_id)
            logger.info(f"Expired session cleaned up: {session_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get conversation manager statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            'active_sessions': len(self.conversations),
            'total_messages': sum(len(conv) for conv in self.conversations.values()),
            'max_history': self.max_history,
            'session_timeout_minutes': self.session_timeout.total_seconds() / 60
        }


