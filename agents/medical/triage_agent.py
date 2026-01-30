"""
Triage Agent
Specialized agent for patient triage and priority assessment
"""

from typing import Optional, Dict, Any
from enum import Enum
from agents.base.agent import BaseAgent, AgentConfig
from agents.base.protocol import AgentMessage
from agents.memory.manager import MemoryManager, MemoryType


class TriagePriority(Enum):
    """Triage priority levels"""
    EMERGENCY = "emergency"  # Immediate attention required
    URGENT = "urgent"  # Within 30 minutes
    SEMI_URGENT = "semi_urgent"  # Within 1-2 hours
    NON_URGENT = "non_urgent"  # Can wait
    

class TriageAgent(BaseAgent):
    """
    AI agent specialized in patient triage and priority assessment
    """
    
    def __init__(self, config: AgentConfig, memory_manager: Optional[MemoryManager] = None):
        """
        Initialize triage agent
        
        Args:
            config: Agent configuration
            memory_manager: Memory manager instance
        """
        super().__init__(config)
        self.memory_manager = memory_manager or MemoryManager()
        
        # Triage criteria
        self.emergency_symptoms = [
            'chest_pain', 'difficulty_breathing', 'severe_bleeding',
            'loss_of_consciousness', 'stroke_symptoms', 'severe_allergic_reaction'
        ]
        
        self.urgent_symptoms = [
            'high_fever', 'severe_pain', 'persistent_vomiting',
            'head_injury', 'severe_burn'
        ]
    
    def _on_start(self) -> None:
        """Initialize agent when started"""
        self.logger.info("Triage agent ready for patient assessment")
        self.update_state('patients_triaged', 0)
    
    def _handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle triage requests
        
        Expected payload:
        {
            'patient_id': str,
            'symptoms': List[str],
            'vital_signs': Dict[str, float],
            'chief_complaint': str
        }
        """
        payload = message.payload
        patient_id = payload.get('patient_id')
        symptoms = payload.get('symptoms', [])
        vital_signs = payload.get('vital_signs', {})
        chief_complaint = payload.get('chief_complaint', '')
        
        if not patient_id:
            return self._create_error_response(message, "Missing patient_id")
        
        # Perform triage assessment
        triage_result = self._assess_priority(symptoms, vital_signs, chief_complaint)
        
        # Store triage in memory
        self.memory_manager.remember(
            agent_id=self.agent_id,
            memory_type=MemoryType.EPISODIC,
            content={
                'patient_id': patient_id,
                'symptoms': symptoms,
                'vital_signs': vital_signs,
                'triage_result': triage_result,
                'assessment_type': 'triage'
            },
            importance=self._get_importance_by_priority(triage_result['priority'])
        )
        
        # Update stats
        count = self.get_state('patients_triaged', 0)
        self.update_state('patients_triaged', count + 1)
        
        # Create response
        response_payload = {
            'patient_id': patient_id,
            'triage_result': triage_result,
            'agent_id': self.agent_id
        }
        
        return self.protocol.create_response(message, response_payload)
    
    def _assess_priority(self, symptoms: List[str], vital_signs: Dict[str, float], 
                        chief_complaint: str) -> Dict[str, Any]:
        """
        Assess patient priority level
        
        Args:
            symptoms: List of symptoms
            vital_signs: Vital sign measurements
            chief_complaint: Patient's chief complaint
            
        Returns:
            Triage assessment results
        """
        # Normalize symptoms
        symptoms_lower = [s.lower().strip().replace(' ', '_') for s in symptoms]
        
        # Check for emergency symptoms
        emergency_match = any(s in symptoms_lower for s in self.emergency_symptoms)
        urgent_match = any(s in symptoms_lower for s in self.urgent_symptoms)
        
        # Check vital signs
        vital_abnormal = self._check_vital_signs(vital_signs)
        
        # Determine priority
        if emergency_match or vital_abnormal.get('critical', False):
            priority = TriagePriority.EMERGENCY
            wait_time = "Immediate"
        elif urgent_match or vital_abnormal.get('abnormal', False):
            priority = TriagePriority.URGENT
            wait_time = "Within 30 minutes"
        elif len(symptoms_lower) > 2:
            priority = TriagePriority.SEMI_URGENT
            wait_time = "Within 1-2 hours"
        else:
            priority = TriagePriority.NON_URGENT
            wait_time = "When available"
        
        return {
            'priority': priority.value,
            'wait_time': wait_time,
            'vital_signs_status': vital_abnormal,
            'reasoning': self._generate_reasoning(symptoms_lower, vital_abnormal, priority),
            'recommended_actions': self._get_recommended_actions(priority)
        }
    
    def _check_vital_signs(self, vital_signs: Dict[str, float]) -> Dict[str, Any]:
        """Check if vital signs are abnormal"""
        status = {'critical': False, 'abnormal': False, 'flags': []}
        
        # Blood pressure
        if 'systolic_bp' in vital_signs:
            if vital_signs['systolic_bp'] > 180 or vital_signs['systolic_bp'] < 90:
                status['critical'] = True
                status['flags'].append('Critical blood pressure')
            elif vital_signs['systolic_bp'] > 140 or vital_signs['systolic_bp'] < 100:
                status['abnormal'] = True
                status['flags'].append('Abnormal blood pressure')
        
        # Heart rate
        if 'heart_rate' in vital_signs:
            if vital_signs['heart_rate'] > 120 or vital_signs['heart_rate'] < 50:
                status['abnormal'] = True
                status['flags'].append('Abnormal heart rate')
        
        # Oxygen saturation
        if 'oxygen_saturation' in vital_signs:
            if vital_signs['oxygen_saturation'] < 90:
                status['critical'] = True
                status['flags'].append('Critical oxygen saturation')
            elif vital_signs['oxygen_saturation'] < 95:
                status['abnormal'] = True
                status['flags'].append('Low oxygen saturation')
        
        # Temperature
        if 'temperature' in vital_signs:
            if vital_signs['temperature'] > 39.5 or vital_signs['temperature'] < 35:
                status['abnormal'] = True
                status['flags'].append('Abnormal temperature')
        
        return status
    
    def _generate_reasoning(self, symptoms: List[str], vital_status: Dict[str, Any],
                           priority: TriagePriority) -> str:
        """Generate reasoning for triage decision"""
        reasons = []
        
        if vital_status.get('critical'):
            reasons.append("Critical vital signs detected")
        
        if vital_status.get('abnormal'):
            reasons.append("Abnormal vital signs present")
        
        emergency_found = [s for s in symptoms if s in self.emergency_symptoms]
        if emergency_found:
            reasons.append(f"Emergency symptoms present: {', '.join(emergency_found)}")
        
        urgent_found = [s for s in symptoms if s in self.urgent_symptoms]
        if urgent_found:
            reasons.append(f"Urgent symptoms present: {', '.join(urgent_found)}")
        
        if not reasons:
            reasons.append(f"Assessed as {priority.value} based on symptom evaluation")
        
        return "; ".join(reasons)
    
    def _get_recommended_actions(self, priority: TriagePriority) -> list[str]:
        """Get recommended actions based on priority"""
        if priority == TriagePriority.EMERGENCY:
            return [
                "Immediate medical attention required",
                "Alert emergency medical team",
                "Prepare emergency equipment",
                "Continuous monitoring"
            ]
        elif priority == TriagePriority.URGENT:
            return [
                "Fast-track to healthcare provider",
                "Monitor vital signs closely",
                "Prepare examination room"
            ]
        elif priority == TriagePriority.SEMI_URGENT:
            return [
                "Schedule for next available provider",
                "Monitor in waiting area",
                "Reassess if condition changes"
            ]
        else:
            return [
                "Standard wait time",
                "Provide comfort measures",
                "Inform if symptoms worsen"
            ]
    
    def _get_importance_by_priority(self, priority: str) -> float:
        """Get memory importance based on triage priority"""
        importance_map = {
            TriagePriority.EMERGENCY.value: 1.0,
            TriagePriority.URGENT.value: 0.8,
            TriagePriority.SEMI_URGENT.value: 0.6,
            TriagePriority.NON_URGENT.value: 0.4
        }
        return importance_map.get(priority, 0.5)
