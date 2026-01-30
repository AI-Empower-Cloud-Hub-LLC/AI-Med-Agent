"""
Diagnosis Agent
Specialized agent for medical diagnosis support
"""

from typing import Optional, Dict, Any, List
from agents.base.agent import BaseAgent, AgentConfig
from agents.base.protocol import AgentMessage, MessageType
from agents.memory.manager import MemoryManager, MemoryType


class DiagnosisAgent(BaseAgent):
    """
    AI agent specialized in analyzing symptoms and suggesting potential diagnoses
    """
    
    def __init__(self, config: AgentConfig, memory_manager: Optional[MemoryManager] = None):
        """
        Initialize diagnosis agent
        
        Args:
            config: Agent configuration
            memory_manager: Memory manager instance
        """
        super().__init__(config)
        self.memory_manager = memory_manager or MemoryManager()
        
        # Medical knowledge base (simplified for demo)
        self.knowledge_base = {
            'fever': ['influenza', 'covid-19', 'bacterial infection', 'viral infection'],
            'cough': ['cold', 'influenza', 'covid-19', 'pneumonia', 'bronchitis'],
            'headache': ['migraine', 'tension headache', 'hypertension', 'dehydration'],
            'fatigue': ['anemia', 'chronic fatigue syndrome', 'depression', 'thyroid disorder'],
            'chest_pain': ['angina', 'heart attack', 'anxiety', 'muscle strain']
        }
    
    def _on_start(self) -> None:
        """Initialize agent when started"""
        self.logger.info("Diagnosis agent ready for medical consultations")
        self.update_state('consultations_count', 0)
    
    def _handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle diagnosis requests
        
        Expected payload:
        {
            'patient_id': str,
            'symptoms': List[str],
            'medical_history': Optional[Dict]
        }
        """
        payload = message.payload
        patient_id = payload.get('patient_id')
        symptoms = payload.get('symptoms', [])
        medical_history = payload.get('medical_history', {})
        
        if not patient_id or not symptoms:
            return self._create_error_response(message, "Missing patient_id or symptoms")
        
        # Analyze symptoms
        diagnosis = self._analyze_symptoms(symptoms, medical_history)
        
        # Store consultation in memory
        self.memory_manager.remember(
            agent_id=self.agent_id,
            memory_type=MemoryType.EPISODIC,
            content={
                'patient_id': patient_id,
                'symptoms': symptoms,
                'diagnosis': diagnosis,
                'consultation_type': 'diagnosis'
            },
            importance=0.8
        )
        
        # Update stats
        count = self.get_state('consultations_count', 0)
        self.update_state('consultations_count', count + 1)
        
        # Create response
        response_payload = {
            'patient_id': patient_id,
            'diagnosis': diagnosis,
            'agent_id': self.agent_id,
            'confidence': diagnosis.get('confidence', 0.0)
        }
        
        return self.protocol.create_response(message, response_payload)
    
    def _analyze_symptoms(self, symptoms: List[str], medical_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze symptoms and generate diagnosis suggestions
        
        Args:
            symptoms: List of reported symptoms
            medical_history: Patient medical history
            
        Returns:
            Diagnosis results
        """
        # Normalize symptoms
        symptoms_lower = [s.lower().strip() for s in symptoms]
        
        # Find matching conditions
        possible_conditions = set()
        matched_symptoms = []
        
        for symptom in symptoms_lower:
            if symptom in self.knowledge_base:
                conditions = self.knowledge_base[symptom]
                possible_conditions.update(conditions)
                matched_symptoms.append(symptom)
        
        # Calculate confidence based on symptom matches
        confidence = len(matched_symptoms) / max(len(symptoms_lower), 1) * 0.8
        
        # Sort conditions by relevance (simplified)
        condition_scores = {}
        for condition in possible_conditions:
            score = sum(1 for symptom in matched_symptoms 
                       if condition in self.knowledge_base.get(symptom, []))
            condition_scores[condition] = score
        
        sorted_conditions = sorted(condition_scores.items(), 
                                  key=lambda x: x[1], reverse=True)
        
        return {
            'symptoms_analyzed': matched_symptoms,
            'possible_conditions': [c[0] for c in sorted_conditions[:5]],
            'confidence': round(confidence, 2),
            'recommendations': self._generate_recommendations(symptoms_lower),
            'disclaimer': 'This is AI-assisted analysis. Please consult a healthcare professional.'
        }
    
    def _generate_recommendations(self, symptoms: List[str]) -> List[str]:
        """Generate recommendations based on symptoms"""
        recommendations = [
            'Consult with a healthcare professional for proper diagnosis'
        ]
        
        if 'fever' in symptoms:
            recommendations.append('Monitor temperature regularly')
            recommendations.append('Stay hydrated')
        
        if 'cough' in symptoms:
            recommendations.append('Rest and avoid irritants')
        
        if 'chest_pain' in symptoms:
            recommendations.append('Seek immediate medical attention if severe')
        
        return recommendations
    
    def get_consultation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent consultation history"""
        memories = self.memory_manager.recall_recent(
            agent_id=self.agent_id,
            memory_type=MemoryType.EPISODIC,
            limit=limit
        )
        return [m.content for m in memories]
