import requests
from typing import List, Dict, Optional


class APIClient:
    
    def __init__(self, base_url: str = "http://127.0.0.1:9000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def check_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_readings(self, limit: Optional[int] = None, device_id: Optional[str] = None) -> List[Dict]:
        try:
            params = {}
            if limit:
                params['limit'] = limit
            if device_id:
                params['device_id'] = device_id
                
            response = self.session.get(f"{self.base_url}/api/readings", params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching readings: {e}")
            return []
    
    def get_alerts(self, limit: Optional[int] = None, device_id: Optional[str] = None) -> List[Dict]:
        try:
            params = {}
            if limit:
                params['limit'] = limit
            if device_id:
                params['device_id'] = device_id
                
            response = self.session.get(f"{self.base_url}/api/alerts", params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching alerts: {e}")
            return []
    
    def get_unique_device_ids(self) -> List[str]:
        try:
            readings = self.get_readings(limit=1000)
            device_ids = list(set(reading.get('device_id', '') for reading in readings))
            return sorted([d for d in device_ids if d])
        except Exception as e:
            print(f"Error getting device IDs: {e}")
            return []
    
    def get_email_log(self, limit: Optional[int] = None) -> List[Dict]:
        try:
            params = {}
            if limit:
                params['limit'] = limit
                
            response = self.session.get(f"{self.base_url}/api/email-log", params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching email log: {e}")
            return []
