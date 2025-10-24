#!/usr/bin/env python3
"""
Soil Sensor Data Viewer
View collected soil sensor data
"""

import json
import os
from datetime import datetime

def view_data(data_file="soil_data.json"):
    """View collected soil sensor data"""
    
    if not os.path.exists(data_file):
        print(f"❌ Data file {data_file} not found")
        return
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    print(f"📊 Soil Sensor Data Viewer")
    print("=" * 60)
    print(f"📁 File: {data_file}")
    print(f"📊 Total records: {len(data)}")
    print("=" * 60)
    
    if not data:
        print("📭 No data available")
        return
    
    # Show summary
    print("\n📈 Data Summary:")
    print(f"   📅 First record: {data[0]['timestamp']}")
    print(f"   📅 Last record: {data[-1]['timestamp']}")
    print(f"   📱 Device: {data[0]['device_id']}")
    if 'application_id' in data[0]:
        print(f"   🏷️  Application: {data[0]['application_id']}")
    else:
        print(f"   🏷️  Application: soil-sensor-saranac")
    
    # Show recent records
    print(f"\n📋 Recent Records (last 5):")
    for i, record in enumerate(data[-5:], 1):
        print(f"\n   Record #{len(data)-5+i}:")
        print(f"   🕐 Time: {record['timestamp']}")
        
        if 'sensor_data' in record:
            sensor = record['sensor_data']
            print(f"   🌱 Sensor Data:")
            print(f"      🔋 Battery: {sensor.get('Bat', 'N/A')}V")
            print(f"      🌡️  Temperature: {sensor.get('TempC_DS18B20', 'N/A')}°C")
            print(f"      🌡️  Soil Temp: {sensor.get('temp_SOIL', 'N/A')}°C")
            print(f"      💧 Soil Moisture: {sensor.get('water_SOIL', 'N/A')}%")
            print(f"      ⚡ Soil Conductivity: {sensor.get('conduct_SOIL', 'N/A')}")
        
        if 'gateway_info' in record:
            gateway = record['gateway_info']
            print(f"   📡 Gateway: {gateway.get('gateway_id', 'N/A')}")
            print(f"   📶 RSSI: {gateway.get('rssi', 'N/A')} dBm")
            print(f"   📶 SNR: {gateway.get('snr', 'N/A')} dB")
    
    # Show all records if requested
    if len(data) <= 10:
        print(f"\n📋 All Records:")
        for i, record in enumerate(data, 1):
            print(f"\n   Record #{i}:")
            print(f"   🕐 Time: {record['timestamp']}")
            if 'sensor_data' in record:
                sensor = record['sensor_data']
                print(f"   🌱 Battery: {sensor.get('Bat', 'N/A')}V")
                print(f"   🌱 Soil Temp: {sensor.get('temp_SOIL', 'N/A')}°C")
                print(f"   🌱 Soil Moisture: {sensor.get('water_SOIL', 'N/A')}%")

def main():
    import sys
    
    # Default to soil_data.json, but allow specifying others
    data_file = "soil_data.json"
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    else:
        # Check which files exist and show options
        import os
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        if len(json_files) > 1:
            print(f"Available JSON files: {', '.join(json_files)}")
            print(f"Using default: {data_file}")
            print(f"To view a specific file: python3 view_data.py <filename>")
    
    view_data(data_file)

if __name__ == "__main__":
    main()
