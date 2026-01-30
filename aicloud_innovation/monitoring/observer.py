"""
Agent Observer
==============

Monitors agent health, performance, and provides observability.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

from ..agents.base_agent import BaseAgent, AgentStatus

# Health check thresholds
FAILURE_RATE_THRESHOLD = 0.3  # 30% failure rate triggers degraded status
INACTIVITY_THRESHOLD_HOURS = 1  # Hours of inactivity before agent marked inactive


class MetricsCollector:
    """
    Collects and aggregates metrics from agents.
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict]] = defaultdict(list)
        self.logger = logging.getLogger("MetricsCollector")
    
    def record_metric(self, agent_id: str, metric_type: str, value: Any, metadata: Dict = None):
        """
        Record a metric for an agent.
        
        Args:
            agent_id: Agent identifier
            metric_type: Type of metric (e.g., 'processing_time', 'task_count')
            value: Metric value
            metadata: Optional additional context
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "type": metric_type,
            "value": value,
            "metadata": metadata or {}
        }
        
        self.metrics[agent_id].append(metric)
    
    def get_metrics(self, agent_id: str, metric_type: Optional[str] = None) -> List[Dict]:
        """
        Get metrics for an agent.
        
        Args:
            agent_id: Agent identifier
            metric_type: Optional filter by metric type
            
        Returns:
            List of metrics
        """
        agent_metrics = self.metrics.get(agent_id, [])
        
        if metric_type:
            return [m for m in agent_metrics if m["type"] == metric_type]
        
        return agent_metrics
    
    def get_aggregate_metrics(self, agent_id: str) -> Dict[str, Any]:
        """
        Get aggregated metrics for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Aggregated metrics
        """
        metrics = self.metrics.get(agent_id, [])
        
        if not metrics:
            return {}
        
        # Aggregate by type
        by_type = defaultdict(list)
        for metric in metrics:
            by_type[metric["type"]].append(metric["value"])
        
        aggregates = {}
        for metric_type, values in by_type.items():
            if all(isinstance(v, (int, float)) for v in values):
                aggregates[metric_type] = {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values)
                }
            else:
                aggregates[metric_type] = {
                    "count": len(values)
                }
        
        return aggregates
    
    def clear_metrics(self, agent_id: Optional[str] = None):
        """
        Clear metrics for an agent or all agents.
        
        Args:
            agent_id: Optional agent ID. If None, clears all metrics.
        """
        if agent_id:
            self.metrics[agent_id].clear()
        else:
            self.metrics.clear()


class AgentObserver:
    """
    Observes and monitors agent health and performance.
    
    Provides real-time monitoring, alerting, and analytics for AI agents.
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.health_checks: Dict[str, Dict] = {}
        self.alerts: List[Dict] = []
        self.logger = logging.getLogger("AgentObserver")
    
    def monitor_agent(self, agent: BaseAgent):
        """
        Monitor an agent's health and performance.
        
        Args:
            agent: Agent to monitor
        """
        status = agent.get_status()
        
        # Record basic metrics
        self.metrics_collector.record_metric(
            agent.agent_id,
            "tasks_completed",
            agent.tasks_completed
        )
        
        self.metrics_collector.record_metric(
            agent.agent_id,
            "tasks_failed",
            agent.tasks_failed
        )
        
        if agent.tasks_completed > 0:
            self.metrics_collector.record_metric(
                agent.agent_id,
                "avg_processing_time",
                agent.total_processing_time / agent.tasks_completed
            )
        
        # Perform health check
        health = self._check_agent_health(agent)
        self.health_checks[agent.agent_id] = health
        
        # Generate alerts if needed
        if health["status"] != "healthy":
            self._generate_alert(agent, health)
    
    def _check_agent_health(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Check agent health status.
        
        Args:
            agent: Agent to check
            
        Returns:
            Health status dictionary
        """
        health = {
            "agent_id": agent.agent_id,
            "agent_name": agent.config.name,
            "status": "healthy",
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if agent is in error state
        if agent.status == AgentStatus.ERROR:
            health["status"] = "unhealthy"
            health["issues"].append("Agent is in ERROR state")
        
        # Check failure rate
        total_tasks = agent.tasks_completed + agent.tasks_failed
        if total_tasks > 0:
            failure_rate = agent.tasks_failed / total_tasks
            if failure_rate > FAILURE_RATE_THRESHOLD:
                health["status"] = "degraded"
                health["issues"].append(f"High failure rate: {failure_rate:.2%}")
        
        # Check if agent is inactive
        time_since_active = datetime.now() - agent.last_active
        if time_since_active > timedelta(hours=INACTIVITY_THRESHOLD_HOURS):
            health["status"] = "inactive"
            health["issues"].append(f"No activity for {time_since_active}")
        
        return health
    
    def _generate_alert(self, agent: BaseAgent, health: Dict[str, Any]):
        """
        Generate alert for unhealthy agent.
        
        Args:
            agent: Agent with issues
            health: Health check results
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": "warning" if health["status"] == "degraded" else "critical",
            "agent_id": agent.agent_id,
            "agent_name": agent.config.name,
            "status": health["status"],
            "issues": health["issues"]
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"Alert generated for agent {agent.config.name}: {health['issues']}")
    
    def get_agent_health(self, agent_id: str) -> Optional[Dict]:
        """
        Get health status for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Health status or None if not monitored
        """
        return self.health_checks.get(agent_id)
    
    def get_all_health_statuses(self) -> List[Dict]:
        """
        Get health status for all monitored agents.
        
        Returns:
            List of health statuses
        """
        return list(self.health_checks.values())
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """
        Get alerts, optionally filtered by severity.
        
        Args:
            severity: Optional severity filter ('warning' or 'critical')
            
        Returns:
            List of alerts
        """
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return self.alerts
    
    def clear_alerts(self, agent_id: Optional[str] = None):
        """
        Clear alerts for an agent or all agents.
        
        Args:
            agent_id: Optional agent ID. If None, clears all alerts.
        """
        if agent_id:
            self.alerts = [a for a in self.alerts if a["agent_id"] != agent_id]
        else:
            self.alerts.clear()
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive monitoring report.
        
        Returns:
            Monitoring report with health, metrics, and alerts
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents_monitored": len(self.health_checks),
            "health_summary": {
                "healthy": sum(1 for h in self.health_checks.values() if h["status"] == "healthy"),
                "degraded": sum(1 for h in self.health_checks.values() if h["status"] == "degraded"),
                "unhealthy": sum(1 for h in self.health_checks.values() if h["status"] == "unhealthy"),
                "inactive": sum(1 for h in self.health_checks.values() if h["status"] == "inactive"),
            },
            "alerts": {
                "total": len(self.alerts),
                "critical": sum(1 for a in self.alerts if a["severity"] == "critical"),
                "warning": sum(1 for a in self.alerts if a["severity"] == "warning"),
            },
            "recent_alerts": self.alerts[-10:] if self.alerts else []
        }
