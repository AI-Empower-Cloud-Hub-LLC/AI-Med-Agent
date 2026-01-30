"""
Metrics Collector
Collects and aggregates agent performance metrics
"""

from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
import json


class MetricsCollector:
    """
    Collects and aggregates metrics from agents
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.started_at = datetime.utcnow()
    
    def record_metric(self, agent_id: str, metric_name: str, value: Any, 
                     metadata: Dict[str, Any] = None) -> None:
        """
        Record a metric for an agent
        
        Args:
            agent_id: Agent ID
            metric_name: Name of the metric
            value: Metric value
            metadata: Additional metadata
        """
        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': agent_id,
            'metric_name': metric_name,
            'value': value,
            'metadata': metadata or {}
        }
        
        self.metrics[agent_id].append(metric)
    
    def get_metrics(self, agent_id: str, metric_name: str = None) -> List[Dict[str, Any]]:
        """
        Get metrics for an agent
        
        Args:
            agent_id: Agent ID
            metric_name: Optional metric name filter
            
        Returns:
            List of metrics
        """
        agent_metrics = self.metrics.get(agent_id, [])
        
        if metric_name:
            agent_metrics = [m for m in agent_metrics if m['metric_name'] == metric_name]
        
        return agent_metrics
    
    def get_aggregate_metrics(self, agent_id: str) -> Dict[str, Any]:
        """
        Get aggregated metrics for an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Aggregated metrics
        """
        agent_metrics = self.metrics.get(agent_id, [])
        
        if not agent_metrics:
            return {}
        
        # Aggregate by metric name
        aggregated = {}
        metric_groups = defaultdict(list)
        
        for metric in agent_metrics:
            metric_groups[metric['metric_name']].append(metric['value'])
        
        for metric_name, values in metric_groups.items():
            # Only aggregate numeric values
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            
            if numeric_values:
                aggregated[metric_name] = {
                    'count': len(numeric_values),
                    'sum': sum(numeric_values),
                    'avg': sum(numeric_values) / len(numeric_values),
                    'min': min(numeric_values),
                    'max': max(numeric_values)
                }
            else:
                aggregated[metric_name] = {
                    'count': len(values),
                    'values': values
                }
        
        return aggregated
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics for all agents"""
        return {
            'started_at': self.started_at.isoformat(),
            'agents': list(self.metrics.keys()),
            'total_metrics': sum(len(metrics) for metrics in self.metrics.values()),
            'metrics_by_agent': {
                agent_id: len(metrics) 
                for agent_id, metrics in self.metrics.items()
            }
        }
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to JSON file"""
        export_data = {
            'exported_at': datetime.utcnow().isoformat(),
            'started_at': self.started_at.isoformat(),
            'metrics': dict(self.metrics)
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def clear_metrics(self, agent_id: str = None) -> None:
        """
        Clear metrics
        
        Args:
            agent_id: Optional agent ID to clear specific agent metrics
        """
        if agent_id:
            if agent_id in self.metrics:
                del self.metrics[agent_id]
        else:
            self.metrics.clear()
