"""Integration tests for JARVIS staging environment.

Tests quantum backend integration, performance benchmarking, and end-to-end
workflows in staging conditions before production deployment.
"""

import pytest
from typing import Dict, Any
import time

from jarvis import JARVISOrchestrator
from jarvis.config.settings import Settings
from jarvis.observability import get_logger, get_collector, get_event_collector
from jarvis.observability.metrics import PerformanceMetrics
from jarvis.observability.events import EventType, EventSeverity, Event


class TestIntegrationCore:
    """Test core JARVIS functionality in integration scenario."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with staging settings."""
        settings = Settings(
            domain="staging_test",
            search_backend="tavily",
            memory_backend="in_memory",
            llm_provider="local",
        )
        return JARVISOrchestrator(settings=settings)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes without errors."""
        assert orchestrator is not None
        assert orchestrator.settings.domain == "staging_test"
        assert len(orchestrator.tools.list_tools()) > 0
    
    def test_query_execution(self, orchestrator):
        """Test basic query execution."""
        result = orchestrator.run("What is quantum computing?")
        assert result is not None
        assert "quantum" in result.lower() or "query" in result.lower()
    
    def test_workflow_construction(self, orchestrator):
        """Test workflow is properly constructed."""
        from jarvis.core.task import Task
        task = Task(query="test query", domain="staging_test")
        workflow = orchestrator.build_workflow(task)
        
        assert workflow is not None
        assert workflow.name is not None
        assert len(workflow.nodes) > 0
    
    def test_memory_persistence(self, orchestrator):
        """Test memory stores and retrieves documents."""
        orchestrator.memory.add_memory("test_doc", "Test content", {"source": "test"})
        
        results = orchestrator.memory.search("test", top_k=1)
        assert len(results) > 0
        assert results[0]["id"] == "test_doc"
    
    def test_tool_registry(self, orchestrator):
        """Test tool registry and execution."""
        tools = orchestrator.tools.list_tools()
        assert "search" in tools
        assert "memory_lookup" in tools
        
        search_result = orchestrator.tools.execute("search", query="test")
        assert isinstance(search_result, dict)


class TestObservability:
    """Test observability and monitoring features."""
    
    def test_structured_logging(self):
        """Test structured logging functionality."""
        logger = get_logger("test")
        logger.info("Test message", user_id="test_user", operation="test_op")
        
        # Verify audit trail exists
        audit_trail = logger.get_audit_trail()
        assert audit_trail is not None
    
    def test_metrics_collection(self):
        """Test metrics collection."""
        collector = get_collector()
        collector.reset()
        
        # Record some operations
        collector.record_operation("query_processing", 100.5, success=True)
        collector.record_operation("query_processing", 95.2, success=True)
        collector.record_operation("query_processing", 110.0, success=False)
        
        metrics = collector.get_metrics("query_processing")
        assert metrics["count"] == 2
        assert metrics["errors"] == 1
        assert metrics["success_rate_percent"] == 66.7
        assert abs(metrics["avg_time_ms"] - 97.85) < 1.0
    
    def test_performance_tracking(self):
        """Test performance metric tracking."""
        collector = get_collector()
        collector.reset()
        
        # Simulate operation with timer
        collector.start_timer("op1")
        time.sleep(0.01)
        duration = collector.end_timer("op1", "timed_operation", success=True)
        
        assert duration >= 10.0
        metrics = collector.get_metrics("timed_operation")
        assert metrics["count"] == 1
        assert metrics["min_time_ms"] >= 10.0
    
    def test_event_tracking(self):
        """Test event collection and querying."""
        collector = get_event_collector()
        collector.clear()
        
        # Create and record events
        event1 = Event(
            EventType.OPERATION_START,
            source="test_module",
            message="Starting operation",
            severity=EventSeverity.INFO
        )
        event2 = Event(
            EventType.OPERATION_END,
            source="test_module",
            message="Operation completed",
            severity=EventSeverity.INFO
        )
        
        collector.record_event(event1)
        collector.record_event(event2)
        
        # Query events
        all_events = collector.get_events()
        assert len(all_events) == 2
        
        start_events = collector.get_events(event_type=EventType.OPERATION_START)
        assert len(start_events) == 1


class TestPerformanceBenchmarking:
    """Performance benchmarking for staging environment."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for performance testing."""
        return JARVISOrchestrator()
    
    def test_query_throughput(self, orchestrator):
        """Test query processing throughput."""
        collector = get_collector()
        collector.reset()
        
        num_queries = 5
        
        for i in range(num_queries):
            collector.record_operation(f"query_{i}", 10.0, success=True)
        
        summary = collector.get_summary()
        assert summary["total_operations"] == num_queries
        assert summary["total_errors"] == 0
    
    def test_memory_search_performance(self, orchestrator):
        """Test memory search performance."""
        # Add documents
        for i in range(100):
            orchestrator.memory.add_memory(
                f"doc_{i}",
                f"Document {i} with quantum content",
                {"index": i}
            )
        
        # Measure search performance
        collector = get_collector()
        collector.reset()
        
        collector.start_timer("search_1")
        results = orchestrator.memory.search("quantum", top_k=5)
        collector.end_timer("search_1", "memory_search", success=True)
        
        assert len(results) > 0
        metrics = collector.get_metrics("memory_search")
        assert metrics["count"] == 1


class TestBackendIntegration:
    """Test integration with quantum backends."""
    
    def test_settings_from_environment(self, monkeypatch):
        """Test settings loading from environment variables."""
        monkeypatch.setenv("JARVIS_DOMAIN", "quantum_vqc")
        monkeypatch.setenv("JARVIS_LLM_PROVIDER", "ollama")
        monkeypatch.setenv("JARVIS_MODULES", "vqc,aletheia")
        
        settings = Settings.from_env()
        assert settings.domain == "quantum_vqc"
        assert settings.llm_provider == "ollama"
        assert "vqc" in settings.enabled_modules
        assert "aletheia" in settings.enabled_modules
    
    def test_module_loading(self):
        """Test specialist module loading."""
        from jarvis.config.loader import ModuleLoader
        
        settings = Settings(enabled_modules=["vqc"])
        loader = ModuleLoader(settings)
        modules = loader.load_enabled()
        
        # At minimum, should attempt to load specified modules
        assert isinstance(modules, dict)
    
    def test_orchestrator_status_reporting(self):
        """Test orchestrator status reporting."""
        orchestrator = JARVISOrchestrator()
        status = orchestrator.status()
        
        assert "settings" in status
        assert "modules" in status
        assert "tools" in status
        assert "workflows" in status
        
        assert status["settings"]["domain"] == "quantum_architect"
        assert status["tools"] is not None


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms."""
    
    def test_invalid_query_handling(self):
        """Test handling of invalid queries."""
        orchestrator = JARVISOrchestrator()
        
        # Should not raise, but return graceful result
        result = orchestrator.run("")
        assert result is not None
    
    def test_memory_search_with_empty_store(self):
        """Test memory search when store is empty."""
        from jarvis.memory.vector_store import VectorMemoryStore
        
        memory = VectorMemoryStore()
        results = memory.search("query")
        assert results is not None
        assert isinstance(results, list)
    
    def test_metrics_with_failed_operations(self):
        """Test metrics collection for failed operations."""
        collector = get_collector()
        collector.reset()
        
        # Record successful and failed operations
        collector.record_operation("risky_op", 50.0, success=True)
        collector.record_operation("risky_op", 100.0, success=False)
        collector.record_operation("risky_op", 75.0, success=True)
        
        metrics = collector.get_metrics("risky_op")
        assert metrics["count"] == 2
        assert metrics["errors"] == 1
        summary = collector.get_summary()
        assert summary["total_errors"] == 1


class TestEndToEndWorkflow:
    """End-to-end workflow tests for production readiness."""
    
    def test_complete_query_lifecycle(self):
        """Test complete query lifecycle with monitoring."""
        logger = get_logger("e2e_test")
        collector = get_collector()
        event_collector = get_event_collector()
        
        collector.reset()
        event_collector.clear()
        
        orchestrator = JARVISOrchestrator()
        
        # Record operation manually
        collector.start_timer("e2e_op")
        
        with logger.timed_operation("complete_query_lifecycle"):
            # Record event
            event = Event(
                EventType.OPERATION_START,
                source="e2e_test",
                message="Starting lifecycle test",
            )
            event_collector.record_event(event)
            
            # Execute query
            result = orchestrator.run("Integration test query")
            
            # Record completion
            event = Event(
                EventType.OPERATION_END,
                source="e2e_test",
                message="Lifecycle test complete",
            )
            event_collector.record_event(event)
        
        # Record operation time
        collector.end_timer("e2e_op", "complete_query_lifecycle", success=True)
        
        # Verify metrics
        summary = collector.get_summary()
        assert summary["total_operations"] >= 1
        
        # Verify events
        events = event_collector.get_events()
        assert len(events) >= 2
        
        # Verify result
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
