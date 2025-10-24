#!/usr/bin/env python3
"""
Simple Soil Sensor Data Collector
Collects soil sensor data from TTN and saves to JSON
"""

import paho.mqtt.client as mqtt
import json
import os
import subprocess
from datetime import datetime

class SoilCollector:
    def __init__(self, data_file="soil_data.json"):
        self.data_file = data_file
        self.data = []
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            print(f"Loaded {len(self.data)} existing records")
        else:
            print("No existing data found")
    
    def fetch_historical_data(self):
        """Fetch historical data using curl"""
        print("Fetching historical data...")
        
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
                print(f"Processing {len(lines)} lines from curl response")
                
                for line in lines:
                    if line.strip():
                        try:
                            json_data = json.loads(line.strip())
                            if 'result' in json_data:
                                result_data = json_data['result']
                                
                                # Check if this data already exists
                                if not self.data_exists(result_data):
                                    print("New historical data found, adding...")
                                    self.add_historical_data(result_data)
                                else:
                                    print("Historical data already exists, skipping...")
                            else:
                                print("No result data in this line")
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON line: {e}")
                            print(f"Line content: {line[:100]}...")
            else:
                print("No historical data available")
                
        except Exception as e:
            print(f"Error fetching historical data: {e}")
    
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
    
    def add_historical_data(self, result_data):
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
        print(f"Added historical data point #{len(self.data)}")
        
        # Print sensor readings
        sensor_data = data_point['sensor_data']
        if sensor_data:
            print(f"Battery: {sensor_data.get('Bat', 'N/A')}V")
            print(f"Soil Temp: {sensor_data.get('temp_SOIL', 'N/A')}C")
            print(f"Soil Moisture: {sensor_data.get('water_SOIL', 'N/A')}%")
            print(f"Conductivity: {sensor_data.get('conduct_SOIL', 'N/A')}")
        
        self.save_data()
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"Saved {len(self.data)} records")
    
    def add_message(self, message):
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
        print(f"Added data point #{len(self.data)}")
        
        # Print sensor readings
        if sensor_data:
            print(f"Battery: {sensor_data.get('Bat', 'N/A')}V")
            print(f"Soil Temp: {sensor_data.get('temp_SOIL', 'N/A')}C")
            print(f"Soil Moisture: {sensor_data.get('water_SOIL', 'N/A')}%")
            print(f"Conductivity: {sensor_data.get('conduct_SOIL', 'N/A')}")
        
        self.save_data()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT")
        client.subscribe("v3/soil-sensor-saranac/devices/lestat-lives/up")
        print("Subscribed to lestat-lives")
    else:
        print(f"Connection failed: {rc}")

def on_message(client, userdata, msg, properties=None):
    print(f"\nNew message received")
    try:
        data = json.loads(msg.payload.decode())
        userdata.add_message(data)
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    print("Soil Sensor Data Collector")
    print("=" * 30)
    
    collector = SoilCollector()
    
    # Step 1: Fetch historical data
    collector.fetch_historical_data()
    
    # Step 2: Start MQTT collection
    print("\nStarting MQTT collection...")
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.user_data_set(collector)
    
    # MQTT settings
    mqtt_host = "localhost"
    mqtt_port = 1883
    mqtt_username = "soil-sensor-saranac@ttn"
    mqtt_password = "NNSXS.BNNIUDOGAMLGYN7HTYF7QRSX2R26F5QNQ254FZY.2YJQHCL3VDNWRVRABLG4XBOUJC5AUHGUFLALIRKH5B6MOBE3T5WQ"
    
    print(f"Connecting to {mqtt_host}:{mqtt_port}")
    
    try:
        client.username_pw_set(mqtt_username, mqtt_password)
        client.connect(mqtt_host, mqtt_port, 60)
        print("Waiting for new messages... (Ctrl+C to stop)")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
        client.disconnect()
        print(f"Final count: {len(collector.data)} records")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
