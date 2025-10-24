#!/usr/bin/env python3
"""
Simple FastAPI server to receive TTN webhooks on Jetson
"""

from fastapi import FastAPI, Request
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTN Webhook Receiver")

@app.post("/webhook/lorawan")
async def receive_lorawan_data(request: Request):
    """Receive TTN webhook data"""
    try:
        # Get the raw JSON payload
        payload = await request.json()
        
        # Log the full payload for debugging
        logger.info(f"Received TTN webhook: {json.dumps(payload, indent=2)}")
        
        # Extract sensor data if it's an uplink message
        if payload.get("name") == "as.up.data.forward":
            decoded_payload = payload.get("data", {}).get("uplink_message", {}).get("decoded_payload", {})
            
            if decoded_payload:
                # Extract meaningful sensor data
                sensor_data = {
                    "timestamp": payload.get("time"),
                    "device_id": payload.get("data", {}).get("end_device_ids", {}).get("device_id"),
                    "battery": decoded_payload.get("Bat"),
                    "soil_moisture": decoded_payload.get("water_SOIL"),
                    "soil_temp": decoded_payload.get("temp_SOIL"),
                    "soil_conductivity": decoded_payload.get("conduct_SOIL"),
                    "air_temp": decoded_payload.get("TempC_DS18B20"),
                    "sensor_flag": decoded_payload.get("Sensor_flag"),
                    "hardware_flag": decoded_payload.get("Hardware_flag")
                }
                
                logger.info(f"Processed sensor data: {sensor_data}")
                
                # Here you can add your LLM processing
                # For example, pass sensor_data to Llama for analysis
                await process_with_llm(sensor_data)
        
        return {"status": "received", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "error": str(e)}

async def process_with_llm(sensor_data):
    """Process sensor data with LLM (Llama)"""
    try:
        # Format data for LLM
        data_text = f"""
        Soil Sensor Reading:
        - Moisture: {sensor_data['soil_moisture']}%
        - Temperature: {sensor_data['soil_temp']}°C
        - Conductivity: {sensor_data['soil_conductivity']}
        - Battery: {sensor_data['battery']}V
        - Timestamp: {sensor_data['timestamp']}
        """
        
        # Here you would call your LLM (Llama) to analyze the data
        # Example: llama_response = call_llama_api(data_text)
        logger.info(f"Ready for LLM processing: {data_text}")
        
        # Save to file or database for processing
        with open(f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(sensor_data, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error in LLM processing: {e}")

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    
    # Run on all interfaces so TTN can reach it
    uvicorn.run(app, host="0.0.0.0", port=8000)
