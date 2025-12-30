"""
IoT Sensor Simulator for Testing
Simulates vitals sensors sending data via HTTP API
"""

import requests
import random
import time
from datetime import datetime


class VitalsSimulator:
    """Simulate health vitals sensor"""
    
    def __init__(self, api_url="http://localhost:8000", user_id="+919876543210"):
        self.api_url = api_url
        self.user_id = user_id
    
    def generate_normal_vitals(self):
        """Generate realistic vitals"""
        return {
            "heart_rate": random.randint(60, 90),
            "spo2": random.uniform(95, 100),
            "temperature": random.uniform(97.0, 99.0)
        }
    
    def generate_fever_vitals(self):
        """Generate vitals indicating fever"""
        return {
            "heart_rate": random.randint(85, 110),
            "spo2": random.uniform(94, 98),
            "temperature": random.uniform(100.5, 102.5)
        }
    
    def generate_emergency_vitals(self):
        """Generate vitals indicating emergency"""
        return {
            "heart_rate": random.randint(120, 150),
            "spo2": random.uniform(88, 93),
            "temperature": random.uniform(103.0, 105.0)
        }
    
    def send_vitals(self, vitals):
        """Send vitals to API"""
        payload = {
            "user_id": self.user_id,
            "vitals": vitals
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/vitals",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Vitals sent successfully")
                print(f"  HR: {vitals['heart_rate']:.1f} bpm")
                print(f"  SpO₂: {vitals['spo2']:.1f}%")
                print(f"  Temp: {vitals['temperature']:.1f}°F")
                
                if result.get('alerts'):
                    print(f"  ⚠️  Alerts: {', '.join(result['alerts'])}")
                
                print()
                return True
            else:
                print(f"✗ Error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("✗ Error: Cannot connect to API. Is the server running?")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


def main():
    """Run simulation"""
    print("=" * 60)
    print("IoT Vitals Sensor Simulator")
    print("=" * 60)
    print()
    
    simulator = VitalsSimulator()
    
    print("Scenario 1: Normal Vitals")
    print("-" * 40)
    vitals = simulator.generate_normal_vitals()
    simulator.send_vitals(vitals)
    time.sleep(2)
    
    print("Scenario 2: Fever Detected")
    print("-" * 40)
    vitals = simulator.generate_fever_vitals()
    simulator.send_vitals(vitals)
    time.sleep(2)
    
    print("Scenario 3: Emergency Situation")
    print("-" * 40)
    vitals = simulator.generate_emergency_vitals()
    simulator.send_vitals(vitals)
    
    print("=" * 60)
    print("Simulation complete!")
    print()


if __name__ == "__main__":
    main()
