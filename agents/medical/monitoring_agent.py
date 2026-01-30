"""
Patient Monitoring Agent
Specialized agent for continuous patient monitoring and alerting
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from agents.base.agent import BaseAgent, AgentConfig
from agents.base.protocol import AgentMessage, MessageType
from agents.memory.manager import MemoryManager, MemoryType


class PatientMonitoringAgent(BaseAgent):
    """
    AI agent specialized in monitoring patient vital signs and detecting anomalies
    """
    
    def __init__(self, config: AgentConfig, memory_manager: Optional[MemoryManager] = None):
        """
        Initialize monitoring agent
        
        Args:
            config: Agent configuration
            memory_manager: Memory manager instance
        """
        super().__init__(config)
        self.memory_manager = memory_manager or MemoryManager()
        
        # Monitoring thresholds
        self.normal_ranges = {
            'heart_rate': (60, 100),
            'systolic_bp': (90, 140),
            'diastolic_bp': (60, 90),
            'oxygen_saturation': (95, 100),
            'temperature': (36.1, 37.8),
            'respiratory_rate': (12, 20)
        }
        
        # Patient monitoring data
        self.monitored_patients: Dict[str, List[Dict[str, Any]]] = {}
    
    def _on_start(self) -> None:
        """Initialize agent when started"""
        self.logger.info("Patient monitoring agent ready")
        self.update_state('patients_monitored', 0)
        self.update_state('alerts_generated', 0)
    
    def _handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle monitoring requests
        
        Expected payload:
        {
            'patient_id': str,
            'vital_signs': Dict[str, float],
            'timestamp': str (ISO format),
            'action': 'record' | 'analyze' | 'get_trends'
        }
        """
        payload = message.payload
        patient_id = payload.get('patient_id')
        action = payload.get('action', 'record')
        
        if not patient_id:
            return self._create_error_response(message, "Missing patient_id")
        
        if action == 'record':
            result = self._record_vitals(patient_id, payload)
        elif action == 'analyze':
            result = self._analyze_patient(patient_id)
        elif action == 'get_trends':
            result = self._get_trends(patient_id)
        else:
            return self._create_error_response(message, f"Unknown action: {action}")
        
        # Create response
        response_payload = {
            'patient_id': patient_id,
            'action': action,
            'result': result,
            'agent_id': self.agent_id
        }
        
        return self.protocol.create_response(message, response_payload)
    
    def _record_vitals(self, patient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record vital signs for a patient
        
        Args:
            patient_id: Patient ID
            data: Vital signs data
            
        Returns:
            Recording result with any alerts
        """
        vital_signs = data.get('vital_signs', {})
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        # Initialize patient monitoring if needed
        if patient_id not in self.monitored_patients:
            self.monitored_patients[patient_id] = []
            count = self.get_state('patients_monitored', 0)
            self.update_state('patients_monitored', count + 1)
        
        # Record vitals
        record = {
            'timestamp': timestamp,
            'vital_signs': vital_signs
        }
        self.monitored_patients[patient_id].append(record)
        
        # Keep only last 100 records per patient
        if len(self.monitored_patients[patient_id]) > 100:
            self.monitored_patients[patient_id] = self.monitored_patients[patient_id][-100:]
        
        # Check for anomalies
        alerts = self._check_anomalies(patient_id, vital_signs)
        
        # Store in memory if there are alerts
        if alerts:
            self.memory_manager.remember(
                agent_id=self.agent_id,
                memory_type=MemoryType.EPISODIC,
                content={
                    'patient_id': patient_id,
                    'vital_signs': vital_signs,
                    'alerts': alerts,
                    'event_type': 'vital_sign_alert'
                },
                importance=0.9
            )
            
            alert_count = self.get_state('alerts_generated', 0)
            self.update_state('alerts_generated', alert_count + len(alerts))
        
        return {
            'recorded': True,
            'alerts': alerts,
            'total_records': len(self.monitored_patients[patient_id])
        }
    
    def _check_anomalies(self, patient_id: str, vital_signs: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Check for anomalies in vital signs
        
        Args:
            patient_id: Patient ID
            vital_signs: Current vital signs
            
        Returns:
            List of alerts
        """
        alerts = []
        
        for metric, value in vital_signs.items():
            if metric in self.normal_ranges:
                min_val, max_val = self.normal_ranges[metric]
                
                if value < min_val:
                    alerts.append({
                        'type': 'below_normal',
                        'metric': metric,
                        'value': value,
                        'normal_range': self.normal_ranges[metric],
                        'severity': self._calculate_severity(metric, value, min_val, max_val)
                    })
                elif value > max_val:
                    alerts.append({
                        'type': 'above_normal',
                        'metric': metric,
                        'value': value,
                        'normal_range': self.normal_ranges[metric],
                        'severity': self._calculate_severity(metric, value, min_val, max_val)
                    })
        
        return alerts
    
    def _calculate_severity(self, metric: str, value: float, min_val: float, max_val: float) -> str:
        """Calculate alert severity"""
        # Calculate how far outside normal range
        if value < min_val:
            deviation = (min_val - value) / min_val
        else:
            deviation = (value - max_val) / max_val
        
        if deviation > 0.3:
            return 'critical'
        elif deviation > 0.15:
            return 'high'
        else:
            return 'moderate'
    
    def _analyze_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Analyze patient monitoring data
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Analysis results
        """
        if patient_id not in self.monitored_patients:
            return {'error': 'Patient not being monitored'}
        
        records = self.monitored_patients[patient_id]
        
        if not records:
            return {'error': 'No monitoring data available'}
        
        # Analyze recent trends
        recent_records = records[-10:]  # Last 10 readings
        
        analysis = {
            'patient_id': patient_id,
            'total_records': len(records),
            'analysis_period': {
                'start': records[0]['timestamp'],
                'end': records[-1]['timestamp']
            },
            'current_status': self._get_current_status(records[-1]['vital_signs']),
            'trends': self._analyze_trends(recent_records)
        }
        
        return analysis
    
    def _get_current_status(self, vital_signs: Dict[str, float]) -> str:
        """Get current patient status based on latest vitals"""
        alerts = self._check_anomalies('temp', vital_signs)
        
        if any(a['severity'] == 'critical' for a in alerts):
            return 'critical'
        elif any(a['severity'] == 'high' for a in alerts):
            return 'warning'
        elif alerts:
            return 'attention'
        else:
            return 'stable'
    
    def _analyze_trends(self, records: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze trends in vital signs"""
        if len(records) < 2:
            return {}
        
        trends = {}
        
        # Get all metrics
        all_metrics = set()
        for record in records:
            all_metrics.update(record['vital_signs'].keys())
        
        # Analyze each metric
        for metric in all_metrics:
            values = [r['vital_signs'].get(metric) for r in records if metric in r['vital_signs']]
            
            if len(values) >= 2:
                # Simple trend detection
                first_half = sum(values[:len(values)//2]) / (len(values)//2)
                second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
                
                diff_percent = ((second_half - first_half) / first_half) * 100
                
                if abs(diff_percent) < 5:
                    trends[metric] = 'stable'
                elif diff_percent > 0:
                    trends[metric] = 'increasing'
                else:
                    trends[metric] = 'decreasing'
        
        return trends
    
    def _get_trends(self, patient_id: str) -> Dict[str, Any]:
        """Get trend data for a patient"""
        if patient_id not in self.monitored_patients:
            return {'error': 'Patient not being monitored'}
        
        records = self.monitored_patients[patient_id]
        
        return {
            'patient_id': patient_id,
            'records_count': len(records),
            'trends': self._analyze_trends(records[-20:]),  # Last 20 readings
            'recent_alerts': self._get_recent_alerts(patient_id)
        }
    
    def _get_recent_alerts(self, patient_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent alerts for a patient"""
        memories = self.memory_manager.recall_recent(
            agent_id=self.agent_id,
            memory_type=MemoryType.EPISODIC,
            limit=limit * 2  # Get more to filter
        )
        
        # Filter for this patient
        patient_alerts = [
            m.content for m in memories 
            if m.content.get('patient_id') == patient_id and m.content.get('event_type') == 'vital_sign_alert'
        ]
        
        return patient_alerts[:limit]
