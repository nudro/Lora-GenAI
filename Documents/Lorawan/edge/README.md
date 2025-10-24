# Edge MQTT Client & Data Collector

This folder contains the MQTT client and data collection system for soil sensor data from TTN.

## Files

- `mqtt_test_client.py` - Basic MQTT test client
- `soil_data_collector.py` - Full data collector with storage
- `view_data.py` - View collected data
- `get_historical_data.py` - Fetch historical data from TTN API

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update MQTT connection settings in the scripts:
   - `mqtt_host`: Your TTN MQTT broker host (usually localhost if running locally)
   - `mqtt_port`: MQTT port (usually 1883)
   - `mqtt_username`: Your application ID (e.g., "soil-sensor-saranac@ttn")
   - `mqtt_password`: Your TTN MQTT API key

## Usage

### Basic Test
```bash
python3 mqtt_test_client.py
```

### Data Collection (Recommended)
```bash
python3 soil_data_collector.py
```
This will:
- Connect to TTN MQTT broker
- Subscribe to soil sensor messages
- Store all data in `soil_sensor_data.json`
- Display sensor readings (battery, temperature, moisture, etc.)

### View Collected Data
```bash
python3 view_data.py
```

### Get Historical Data
```bash
python3 get_historical_data.py
```

## Data Storage

- **Real-time data**: Stored in `soil_sensor_data.json`
- **Historical data**: Stored in `historical_soil_data.json`
- **Data format**: JSON with timestamps, sensor readings, and metadata

## Sensor Data Fields

- 🔋 **Battery**: Battery voltage
- 🌡️ **Temperature**: Air temperature (°C)
- 🌡️ **Soil Temperature**: Soil temperature (°C)
- 💧 **Soil Moisture**: Soil moisture percentage
- ⚡ **Soil Conductivity**: Soil electrical conductivity

Press Ctrl+C to stop any client.
