import pytest
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database import GridIntelligence

class TestGridIntelligence:
    """Integration tests for SQLite Database Layer"""

    @pytest.fixture
    def grid(self, tmp_path):
        # Use a temporary database file created by pytest
        db_path = tmp_path / "test_namo.db"
        return GridIntelligence(str(db_path))

    def test_store_and_retrieve_session(self, grid):
        """Test storing conversation and retrieving history"""
        session_id = "sess_test_001"
        data = {
            "user_id": "user_123",
            "session_id": session_id,
            "message": "I feel sad",
            "response": "I am here for you",
            "risk_level": "moderate",
            "dharma_score": 0.5,
            "multimodal": {"combined_risk": 0.4}
        }

        # Store data
        grid.store_sovereign(data)

        # Retrieve history
        history = grid.get_session_history(session_id)
        
        assert len(history) == 1
        assert history[0]['message'] == "I feel sad"
        assert history[0]['risk'] == "moderate"
        assert history[0]['dharma'] == 0.5

    def test_crisis_alert_creation(self, grid):
        """Test crisis alert generation and retrieval"""
        data = {
            "user_id": "user_crisis",
            "session_id": "sess_crisis",
            "risk_level": "severe"
        }

        # Create alert
        prompts = grid.create_crisis_alert(data)
        
        # Verify alerts
        alerts = grid.get_alerts("sess_crisis")
        assert len(alerts) == 1
        assert alerts[0]['risk'] == "severe"
        assert isinstance(prompts, list)