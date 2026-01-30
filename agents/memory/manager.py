"""
Memory Manager
High-level memory management for agents
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from agents.memory.store import MemoryStore, MemoryEntry


class MemoryType(Enum):
    """Types of memory"""
    EPISODIC = "episodic"  # Event-based memories
    SEMANTIC = "semantic"  # Knowledge and facts
    PROCEDURAL = "procedural"  # Skills and procedures
    WORKING = "working"  # Short-term working memory


class MemoryManager:
    """
    Manages agent memories with different types and retrieval strategies
    """
    
    def __init__(self, store: Optional[MemoryStore] = None):
        """
        Initialize memory manager
        
        Args:
            store: Memory store instance (creates new if not provided)
        """
        self.store = store or MemoryStore()
        self.working_memory_ttl = timedelta(hours=1)  # Working memory expires after 1 hour
    
    def remember(self, agent_id: str, memory_type: MemoryType, 
                 content: Dict[str, Any], importance: float = 0.5,
                 metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a new memory
        
        Args:
            agent_id: ID of the agent
            memory_type: Type of memory
            content: Memory content
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        memory = MemoryEntry(
            agent_id=agent_id,
            memory_type=memory_type.value,
            content=content,
            importance=importance,
            metadata=metadata or {}
        )
        
        return self.store.store(memory)
    
    def recall(self, agent_id: str, memory_id: str) -> Optional[MemoryEntry]:
        """
        Recall a specific memory
        
        Args:
            agent_id: ID of the agent
            memory_id: ID of the memory
            
        Returns:
            Memory entry if found
        """
        memory = self.store.retrieve(memory_id)
        if memory and memory.agent_id == agent_id:
            return memory
        return None
    
    def recall_recent(self, agent_id: str, memory_type: Optional[MemoryType] = None,
                     limit: int = 10) -> List[MemoryEntry]:
        """
        Recall recent memories
        
        Args:
            agent_id: ID of the agent
            memory_type: Filter by memory type
            limit: Maximum number of memories
            
        Returns:
            List of recent memories
        """
        type_filter = memory_type.value if memory_type else None
        memories = self.store.search(agent_id, memory_type=type_filter)
        return memories[:limit]
    
    def recall_important(self, agent_id: str, min_importance: float = 0.7,
                        limit: int = 10) -> List[MemoryEntry]:
        """
        Recall important memories
        
        Args:
            agent_id: ID of the agent
            min_importance: Minimum importance threshold
            limit: Maximum number of memories
            
        Returns:
            List of important memories
        """
        memories = self.store.search(agent_id, min_importance=min_importance)
        return memories[:limit]
    
    def forget(self, agent_id: str, memory_id: str) -> bool:
        """
        Forget (delete) a memory
        
        Args:
            agent_id: ID of the agent
            memory_id: ID of the memory
            
        Returns:
            True if memory was deleted
        """
        memory = self.store.retrieve(memory_id)
        if memory and memory.agent_id == agent_id:
            return self.store.delete(memory_id)
        return False
    
    def clear_working_memory(self, agent_id: str) -> int:
        """
        Clear expired working memory
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Number of memories cleared
        """
        working_memories = self.store.search(agent_id, memory_type=MemoryType.WORKING.value)
        cutoff_time = datetime.utcnow() - self.working_memory_ttl
        
        count = 0
        for memory in working_memories:
            if memory.timestamp < cutoff_time:
                if self.store.delete(memory.memory_id):
                    count += 1
        
        return count
    
    def get_memory_summary(self, agent_id: str) -> Dict[str, Any]:
        """
        Get a summary of agent's memories
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Memory summary statistics
        """
        all_memories = self.store.retrieve_by_agent(agent_id)
        
        summary = {
            'total_memories': len(all_memories),
            'by_type': {},
            'average_importance': 0.0,
            'most_recent': None,
            'oldest': None
        }
        
        if all_memories:
            # Count by type
            for memory_type in MemoryType:
                type_memories = [m for m in all_memories if m.memory_type == memory_type.value]
                summary['by_type'][memory_type.value] = len(type_memories)
            
            # Calculate average importance
            summary['average_importance'] = sum(m.importance for m in all_memories) / len(all_memories)
            
            # Most recent and oldest
            summary['most_recent'] = all_memories[0].timestamp.isoformat()
            summary['oldest'] = all_memories[-1].timestamp.isoformat()
        
        return summary
