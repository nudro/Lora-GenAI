#!/usr/bin/env python3
"""
Jetson Orin Hybrid Soil Sensor Data Collector
Fetches historical data on startup, then continues with real-time MQTT
"""

import paho.mqtt.client as mqtt
import json
import os
import subprocess
from datetime import datetime

class OrinHybridCollector:
    def __init__(self, data_file="orin_hybrid_data.json"):
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
            "-H", "Authorization: Bearer YOUR_TTN_API_KEY",
            "-H", "Accept: text/event-stream",
            "-d", "last=12h"
        ]
        
        try:
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse multiple JSON objects (one per line)
                lines = result.stdout.strip().split('\n')
                print(f"Processing {len(lines)} lines from API response")
                
                new_count = 0
                for line in lines:
                    if line.strip():
                        try:
                            json_data = json.loads(line.strip())
                            if 'result' in json_data:
                                result_data = json_data['result']
                                
                                # Check if this data already exists
                                if not self.data_exists(result_data):
                                    print("New historical data found, adding...")
                                    self.add_historical_record(result_data)
                                    new_count += 1
                                else:
                                    print("Historical data already exists, skipping...")
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON line: {e}")
                
                print(f"Added {new_count} new historical records")
                return new_count
            else:
                print("No historical data available from API")
                return 0
                
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return 0
    
    def data_exists(self, new_data):
        """Check if data already exists based on received_at timestamp"""
        new_timestamp = new_data.get('received_at', '')
        
        for existing in self.data:
            if 'raw_message' in existing:
                raw = existing['raw_message']
                if 'data' in raw and 'received_at' in raw['data']:
                    if raw['data']['received_at'] == new_timestamp:
                        return True
        return False
    
    def add_historical_record(self, result_data):
        """Add historical data to collection"""
        timestamp = result_data.get('received_at', datetime.now().isoformat())
        
        # Create data point in same format as MQTT messages
        data_point = {
            "timestamp": timestamp,
            "device_id": result_data.get('end_device_ids', {}).get('device_id', 'lestat-lives'),
            "sensor_data": result_data.get('uplink_message', {}).get('decoded_payload', {}),
            "raw_message": {"data": result_data}
        }
        
        self.data.append(data_point)
        print(f"Added historical record #{len(self.data)}")
        
        # Print sensor readings
        sensor_data = data_point['sensor_data']
        if sensor_data:
            print(f"  Battery: {sensor_data.get('Bat', 'N/A')}V")
            print(f"  Soil Temp: {sensor_data.get('temp_SOIL', 'N/A')}C")
            print(f"  Soil Moisture: {sensor_data.get('water_SOIL', 'N/A')}%")
            print(f"  Conductivity: {sensor_data.get('conduct_SOIL', 'N/A')}")
    
    def add_mqtt_message(self, message):
        """Add new MQTT message to collection"""
        timestamp = datetime.now().isoformat()
        
        # Extract device info and sensor data (always in same format)
        device_id = message["data"]["end_device_ids"].get("device_id", "unknown")
        sensor_data = message["data"]["uplink_message"].get("decoded_payload", {})
        
        # Create data point
        data_point = {
            "timestamp": timestamp,
            "device_id": device_id,
            "sensor_data": sensor_data,
            "raw_message": message
        }
        
        self.data.append(data_point)
        print(f"Added MQTT record #{len(self.data)}")
        
        # Print sensor readings
        if sensor_data:
            print(f"  Battery: {sensor_data.get('Bat', 'N/A')}V")
            print(f"  Soil Temp: {sensor_data.get('temp_SOIL', 'N/A')}C")
            print(f"  Soil Moisture: {sensor_data.get('water_SOIL', 'N/A')}%")
            print(f"  Conductivity: {sensor_data.get('conduct_SOIL', 'N/A')}")
        
        self.save_data()

def on_connect(client, userdata, flags, rc, properties=None):
    """Called when the client connects to the MQTT broker"""
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("v3/soil-sensor-saranac/devices/lestat-lives/up")
        print("Subscribed to lestat-lives device")
    else:
        print(f"MQTT connection failed: {rc}")

def on_message(client, userdata, msg, properties=None):
    """Called when a message is received"""
    print(f"\nNew MQTT message received")
    try:
        data = json.loads(msg.payload.decode())
        userdata.add_mqtt_message(data)
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def on_disconnect(client, userdata, rc, properties=None):
    """Called when the client disconnects"""
    if rc != 0:
        print(f"Unexpected MQTT disconnection: {rc}")
    else:
        print("Disconnected from MQTT broker")

def main():
    print("Jetson Orin Hybrid Soil Sensor Data Collector")
    print("=" * 60)
    
    collector = OrinHybridCollector()
    
    # Step 1: Fetch historical data on startup
    print("Step 1: Fetching historical data on startup...")
    historical_count = collector.fetch_historical_data()
    
    if historical_count > 0:
        collector.save_data()
        print(f"Historical data collection complete: {historical_count} new records")
    else:
        print("No new historical data found")
    
    print(f"\nCurrent total records: {len(collector.data)}")
    
    # Step 2: Start MQTT real-time collection
    print("\nStep 2: Starting MQTT real-time collection...")
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.user_data_set(collector)
    
    # MQTT settings
    mqtt_host = "YOUR_LOCAL_COMPUTER_IP"  # Replace with your local computer's IP address
    mqtt_port = 1883
    mqtt_username = "soil-sensor-saranac@ttn"
    mqtt_password = "YOUR_MQTT_PASSWORD"
    
    print(f"Connecting to MQTT broker at {mqtt_host}:{mqtt_port}")
    
    try:
        client.username_pw_set(mqtt_username, mqtt_password)
        client.connect(mqtt_host, mqtt_port, 60)
        print("Waiting for real-time messages... (Ctrl+C to stop)")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping hybrid collector...")
        client.disconnect()
        print(f"Final count: {len(collector.data)} records")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
