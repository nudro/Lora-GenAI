#!/usr/bin/env python3
"""
Jetson Orin Soil Sensor Data Collector
Fetches historical data, compares with local JSON, and reconciles
"""

import json
import os
import subprocess
from datetime import datetime

class OrinSoilCollector:
    def __init__(self, data_file="orin_soil_data.json"):
        self.data_file = data_file
        self.data = []
        self.load_data()
    
    def load_data(self):
        """Load existing data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            print(f"Loaded {len(self.data)} existing records from {self.data_file}")
        else:
            print(f"No existing data found, starting fresh")
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"Saved {len(self.data)} records to {self.data_file}")
    
    def fetch_historical_data(self):
        """Fetch historical data using curl"""
        print("Fetching historical data from TTN...")
        
        curl_command = [
            "curl", "-G",
            "https://nam1.cloud.thethings.network/api/v3/as/applications/soil-sensor-saranac/devices/lestat-lives/packages/storage/uplink_message",
            "-H", "Authorization: Bearer NNSXS.4NHBK6Y6LZZRCT6RBWFLZT7MSFWWMRTA3YXENSI.CBAILAOXXHT7T2SS2J66I4QA2PS2BWP32QZY6PVCYATC5LYLQ3LQ",
            "-H", "Accept: text/event-stream",
            "-d", "last=12h"
        ]
        
        try:
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse multiple JSON objects (one per line)
                lines = result.stdout.strip().split('\n')
                print(f"Processing {len(lines)} lines from API response")
                
                new_records = []
                for line in lines:
                    if line.strip():
                        try:
                            json_data = json.loads(line.strip())
                            if 'result' in json_data:
                                result_data = json_data['result']
                                new_records.append(result_data)
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON line: {e}")
                
                print(f"Found {len(new_records)} records from API")
                return new_records
            else:
                print("No historical data available from API")
                return []
                
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return []
    
    def compare_and_reconcile(self, api_records):
        """Compare API data with local data and reconcile"""
        print("Comparing API data with local data...")
        
        # Get existing timestamps
        existing_timestamps = set()
        for record in self.data:
            if 'raw_message' in record and 'data' in record['raw_message']:
                received_at = record['raw_message']['data'].get('received_at', '')
                if received_at:
                    existing_timestamps.add(received_at)
        
        print(f"Found {len(existing_timestamps)} existing timestamps")
        
        # Check each API record
        new_count = 0
        for api_record in api_records:
            received_at = api_record.get('received_at', '')
            
            if received_at not in existing_timestamps:
                print(f"New record found: {received_at}")
                self.add_new_record(api_record)
                new_count += 1
            else:
                print(f"Record already exists: {received_at}")
        
        print(f"Added {new_count} new records")
        return new_count
    
    def add_new_record(self, api_record):
        """Add a new record from API"""
        timestamp = api_record.get('received_at', datetime.now().isoformat())
        
        # Create data point in same format as MQTT messages
        data_point = {
            "timestamp": timestamp,
            "device_id": api_record.get('end_device_ids', {}).get('device_id', 'lestat-lives'),
            "sensor_data": api_record.get('uplink_message', {}).get('decoded_payload', {}),
            "raw_message": {"data": api_record}
        }
        
        self.data.append(data_point)
        print(f"Added record #{len(self.data)}")
        
        # Print sensor readings
        sensor_data = data_point['sensor_data']
        if sensor_data:
            print(f"  Battery: {sensor_data.get('Bat', 'N/A')}V")
            print(f"  Soil Temp: {sensor_data.get('temp_SOIL', 'N/A')}C")
            print(f"  Soil Moisture: {sensor_data.get('water_SOIL', 'N/A')}%")
            print(f"  Conductivity: {sensor_data.get('conduct_SOIL', 'N/A')}")
    
    def run_collection(self):
        """Main collection process"""
        print("Jetson Orin Soil Sensor Data Collector")
        print("=" * 50)
        
        # Step 1: Load existing data
        print(f"Step 1: Loaded {len(self.data)} existing records")
        
        # Step 2: Fetch historical data from API
        print("\nStep 2: Fetching historical data from API...")
        api_records = self.fetch_historical_data()
        
        if not api_records:
            print("No new data available")
            return
        
        # Step 3: Compare and reconcile
        print("\nStep 3: Comparing and reconciling data...")
        new_count = self.compare_and_reconcile(api_records)
        
        # Step 4: Save updated data
        if new_count > 0:
            print(f"\nStep 4: Saving {new_count} new records...")
            self.save_data()
        else:
            print("\nStep 4: No new records to save")
        
        print(f"\nFinal status:")
        print(f"  Total records: {len(self.data)}")
        print(f"  New records added: {new_count}")

def main():
    collector = OrinSoilCollector()
    collector.run_collection()

if __name__ == "__main__":
    main()
