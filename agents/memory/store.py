"""
Memory Store
Persistent storage for agent memories and state
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import uuid


@dataclass
class MemoryEntry:
    """A single memory entry"""
    
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    memory_type: str = "episodic"
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    importance: float = 0.5  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'memory_id': self.memory_id,
            'agent_id': self.agent_id,
            'memory_type': self.memory_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'importance': self.importance,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        return cls(
            memory_id=data.get('memory_id', str(uuid.uuid4())),
            agent_id=data.get('agent_id', ''),
            memory_type=data.get('memory_type', 'episodic'),
            content=data.get('content', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow(),
            importance=data.get('importance', 0.5),
            metadata=data.get('metadata', {})
        )


class MemoryStore:
    """
    In-memory storage for agent memories
    Can be extended to use databases or cloud storage
    """
    
    def __init__(self):
        self.memories: Dict[str, MemoryEntry] = {}
        self.agent_memories: Dict[str, List[str]] = {}  # agent_id -> [memory_ids]
    
    def store(self, memory: MemoryEntry) -> str:
        """
        Store a memory entry
        
        Args:
            memory: MemoryEntry to store
            
        Returns:
            Memory ID
        """
        self.memories[memory.memory_id] = memory
        
        if memory.agent_id not in self.agent_memories:
            self.agent_memories[memory.agent_id] = []
        
        self.agent_memories[memory.agent_id].append(memory.memory_id)
        return memory.memory_id
    
    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID"""
        return self.memories.get(memory_id)
    
    def retrieve_by_agent(self, agent_id: str, limit: Optional[int] = None) -> List[MemoryEntry]:
        """
        Retrieve all memories for an agent
        
        Args:
            agent_id: Agent ID
            limit: Maximum number of memories to return (most recent first)
            
        Returns:
            List of memory entries
        """
        memory_ids = self.agent_memories.get(agent_id, [])
        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]
        
        # Sort by timestamp (most recent first)
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        
        if limit:
            memories = memories[:limit]
        
        return memories
    
    def search(self, agent_id: str, memory_type: Optional[str] = None,
               min_importance: float = 0.0) -> List[MemoryEntry]:
        """
        Search memories with filters
        
        Args:
            agent_id: Agent ID
            memory_type: Filter by memory type
            min_importance: Minimum importance threshold
            
        Returns:
            List of matching memory entries
        """
        memories = self.retrieve_by_agent(agent_id)
        
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        memories = [m for m in memories if m.importance >= min_importance]
        
        return memories
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory"""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            del self.memories[memory_id]
            
            if memory.agent_id in self.agent_memories:
                self.agent_memories[memory.agent_id] = [
                    mid for mid in self.agent_memories[memory.agent_id] 
                    if mid != memory_id
                ]
            
            return True
        return False
    
    def clear_agent_memories(self, agent_id: str) -> int:
        """
        Clear all memories for an agent
        
        Returns:
            Number of memories cleared
        """
        memory_ids = self.agent_memories.get(agent_id, [])
        count = 0
        
        for memory_id in memory_ids:
            if self.delete(memory_id):
                count += 1
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics"""
        return {
            'total_memories': len(self.memories),
            'agents_with_memories': len(self.agent_memories),
            'memory_types': list(set(m.memory_type for m in self.memories.values()))
        }
