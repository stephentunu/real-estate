"""
Performance testing configuration for Jaston Real Estate backend.

This file defines load testing scenarios using Locust to simulate
realistic user behavior and measure system performance under load.
"""

from typing import Any
import random
from locust import HttpUser, task, between


class PropertyManagementUser(HttpUser):
    """
    Simulates a typical property management user workflow.
    
    This user class represents common interactions with the Jaston Real Estate
    platform, including authentication, property browsing, and basic operations.
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self) -> None:
        """Initialize user session and authenticate."""
        # Simulate user login
        self.login()
    
    def login(self) -> None:
        """Authenticate user for testing session."""
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "perf_user_1",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            # Store authentication token for subsequent requests
            token = response.json().get("access_token")
            if token:
                self.client.headers.update({"Authorization": f"Bearer {token}"})
    
    @task(3)
    def browse_properties(self) -> None:
        """Test property listing and browsing performance."""
        # Get property list
        self.client.get("/api/v1/properties/")
        
        # Get property details for a random property
        property_id = random.randint(1, 10)
        self.client.get(f"/api/v1/properties/{property_id}/")
    
    @task(2)
    def search_properties(self) -> None:
        """Test property search functionality."""
        search_params = {
            "location": random.choice(["downtown", "suburbs", "city center"]),
            "max_rent": random.choice([1000, 1500, 2000, 2500]),
            "bedrooms": random.choice([1, 2, 3, 4])
        }
        
        self.client.get("/api/v1/properties/search/", params=search_params)
    
    @task(1)
    def view_user_profile(self) -> None:
        """Test user profile access."""
        self.client.get("/api/v1/users/profile/")
    
    @task(1)
    def check_notifications(self) -> None:
        """Test notification system performance."""
        self.client.get("/api/v1/notifications/")


class LandlordUser(HttpUser):
    """
    Simulates landlord-specific workflows.
    
    This user class focuses on property management operations
    that landlords typically perform.
    """
    
    wait_time = between(2, 5)  # Landlords typically spend more time per action
    
    def on_start(self) -> None:
        """Initialize landlord session."""
        self.login()
    
    def login(self) -> None:
        """Authenticate landlord user."""
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "perf_landlord",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                self.client.headers.update({"Authorization": f"Bearer {token}"})
    
    @task(3)
    def manage_properties(self) -> None:
        """Test property management operations."""
        # View owned properties
        self.client.get("/api/v1/properties/owned/")
        
        # Check property analytics
        property_id = random.randint(1, 5)
        self.client.get(f"/api/v1/properties/{property_id}/analytics/")
    
    @task(2)
    def review_applications(self) -> None:
        """Test lease application review process."""
        self.client.get("/api/v1/leases/applications/")
        
        # View specific application
        app_id = random.randint(1, 10)
        self.client.get(f"/api/v1/leases/applications/{app_id}/")
    
    @task(1)
    def maintenance_requests(self) -> None:
        """Test maintenance request management."""
        self.client.get("/api/v1/maintenance/requests/")


class TenantUser(HttpUser):
    """
    Simulates tenant-specific workflows.
    
    This user class focuses on tenant operations like
    lease management and maintenance requests.
    """
    
    wait_time = between(1, 4)
    
    def on_start(self) -> None:
        """Initialize tenant session."""
        self.login()
    
    def login(self) -> None:
        """Authenticate tenant user."""
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "perf_tenant",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                self.client.headers.update({"Authorization": f"Bearer {token}"})
    
    @task(3)
    def view_lease_info(self) -> None:
        """Test lease information access."""
        self.client.get("/api/v1/leases/current/")
        
        # Check payment history
        self.client.get("/api/v1/payments/history/")
    
    @task(2)
    def submit_maintenance_request(self) -> None:
        """Test maintenance request submission."""
        # View maintenance request form data
        self.client.get("/api/v1/maintenance/categories/")
        
        # Submit a test maintenance request (read-only for performance testing)
        self.client.get("/api/v1/maintenance/requests/")
    
    @task(1)
    def check_messages(self) -> None:
        """Test messaging system performance."""
        self.client.get("/api/v1/messages/")


class APIStressTest(HttpUser):
    """
    High-frequency API stress testing.
    
    This user class performs rapid API calls to test
    system performance under heavy load.
    """
    
    wait_time = between(0.1, 0.5)  # Very short wait times for stress testing
    
    @task
    def rapid_api_calls(self) -> None:
        """Perform rapid API calls to stress test the system."""
        endpoints = [
            "/api/v1/properties/",
            "/api/v1/health/",
            "/api/v1/cities/",
            "/api/v1/properties/featured/"
        ]
        
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)


# Performance test configuration
class PerformanceTestConfig:
    """Configuration class for performance testing scenarios."""
    
    # User distribution for different test scenarios
    USER_CLASSES = [
        PropertyManagementUser,
        LandlordUser, 
        TenantUser,
        APIStressTest
    ]
    
    # Test scenarios with different user loads
    SCENARIOS = {
        "light_load": {
            "users": 10,
            "spawn_rate": 2,
            "duration": "2m"
        },
        "medium_load": {
            "users": 50,
            "spawn_rate": 5,
            "duration": "5m"
        },
        "heavy_load": {
            "users": 100,
            "spawn_rate": 10,
            "duration": "10m"
        },
        "stress_test": {
            "users": 200,
            "spawn_rate": 20,
            "duration": "15m"
        }
    }
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        "max_response_time": 2000,  # 2 seconds
        "avg_response_time": 500,   # 500ms
        "error_rate": 0.01,         # 1% error rate
        "requests_per_second": 100  # Minimum RPS
    }


if __name__ == "__main__":
    """
    Run performance tests locally.
    
    Usage:
        python locustfile.py
        
    Then open http://localhost:8089 to configure and start tests.
    """
    import os
    from locust import main
    
    # Set default host if not provided
    if not os.environ.get("LOCUST_HOST"):
        os.environ["LOCUST_HOST"] = "http://localhost:8000"
    
    main.main()