"""
Agentic Soil Sensor Monitor with Local LLM
Uses LangChain ReAct agent with local LLM (Ollama) for autonomous monitoring
"""

import json
import os
from datetime import datetime
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from typing import List, Dict, Any
import pandas as pd
import numpy as np

# Try to use Ollama local LLM, fallback to OpenAI if needed
try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: langchain_community not installed. Install with: pip install langchain-community")
    print("Falling back to OpenAI...")
    from langchain_openai import ChatOpenAI

# API Key path (for OpenAI fallback)
API_KEY_PATH = "/Users/catherineordun/Documents/Keys/openai_key.txt"

# Alert state tracking (in production, use a database)
ALERT_STATE = {
    'last_email_sent': None,
    'email_cooldown_seconds': 3600,  # 1 hour
    'alert_history': []
}

def load_api_key():
    """Load API key from file (for OpenAI fallback)."""
    if os.path.exists(API_KEY_PATH):
        with open(API_KEY_PATH, 'r') as f:
            return f.read().strip()
    return None

class SoilSensorTools:
    """Collection of tools for the agent to use"""
    
    @staticmethod
    def check_threshold(value: float, threshold: float, sensor_name: str) -> str:
        """Check if a sensor value exceeds a threshold"""
        is_critical = value < threshold
        status = "CRITICAL" if is_critical else "OK"
        message = f"{sensor_name} = {value:.2f}, Threshold = {threshold:.2f}. Status: {status}"
        
        ALERT_STATE['alert_history'].append({
            'timestamp': datetime.now().isoformat(),
            'sensor': sensor_name,
            'value': value,
            'threshold': threshold,
            'status': status
        })
        
        return message
    
    @staticmethod
    def send_email_alert(reason: str, data: Dict) -> str:
        """Send an email alert (simulated)"""
        now = datetime.now()
        last_sent = ALERT_STATE['last_email_sent']
        
        # Check cooldown period
        if last_sent:
            seconds_elapsed = (now - last_sent).total_seconds()
            if seconds_elapsed < ALERT_STATE['email_cooldown_seconds']:
                remaining = int(ALERT_STATE['email_cooldown_seconds'] - seconds_elapsed)
                return f"Email cooldown active. Wait {remaining} seconds before next email."
        
        # Send email (simulated)
        email_content = f"""
        SOIL SENSOR ALERT
        
        Reason: {reason}
        Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}
        
        Current Reading:
        - Battery: {data.get('Bat', 'N/A')}V
        - Soil Temperature: {data.get('temp_SOIL', 'N/A')}°C
        - Soil Moisture: {data.get('water_SOIL', 'N/A')}%
        - Conductivity: {data.get('conduct_SOIL', 'N/A')}
        
        Action Required: Please check sensor immediately.
        """
        
        # Simulate sending email
        print("\n" + "="*60)
        print(email_content)
        print("="*60 + "\n")
        
        ALERT_STATE['last_email_sent'] = now
        
        return f"Email alert sent. Reason: {reason}"
    
    @staticmethod
    def forecast_temperature(data_points: List[float], hours_ahead: int = 6) -> str:
        """Simple linear forecast (in production, use ARIMA/prophet)"""
        if len(data_points) < 3:
            return "Not enough data for forecasting"
        
        # Simple linear trend
        x = np.array(range(len(data_points)))
        y = np.array(data_points)
        
        # Linear regression
        coeffs = np.polyfit(x, y, 1)
        trend = coeffs[0]
        
        # Forecast
        future_value = data_points[-1] + (trend * hours_ahead)
        
        direction = "increasing" if trend > 0 else "decreasing"
        
        return f"Forecast: {future_value:.2f} in {hours_ahead} hours. Trend: {direction} ({trend:.3f}/hour)"
    
    @staticmethod
    def calculate_statistics(values: List[float], sensor_name: str) -> str:
        """Calculate basic statistics"""
        if not values:
            return "No data available"
        
        stats = {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'count': len(values)
        }
        
        return f"{sensor_name} Stats: Mean={stats['mean']:.2f}, Std={stats['std']:.2f}, Min={stats['min']:.2f}, Max={stats['max']:.2f}, Count={stats['count']}"
    
    @staticmethod
    def check_alert_cooldown() -> str:
        """Check when the last alert was sent"""
        if ALERT_STATE['last_email_sent'] is None:
            return "No alerts sent yet"
        
        seconds_since = (datetime.now() - ALERT_STATE['last_email_sent']).total_seconds()
        minutes_ago = seconds_since / 60
        
        return f"Last alert sent {minutes_ago:.1f} minutes ago"


def check_threshold_tool(value: str, threshold: str, sensor_name: str = "Sensor") -> str:
    """Check if a sensor value exceeds a threshold"""
    try:
        return SoilSensorTools.check_threshold(float(value), float(threshold), sensor_name)
    except:
        return "Invalid input format. Use: value,threshold,sensor_name"

def send_email_tool(reason: str) -> str:
    """Send an email alert with a reason"""
    data = {"Bat": 3.6, "temp_SOIL": 18.7, "water_SOIL": 4.8, "conduct_SOIL": 5}
    return SoilSensorTools.send_email_alert(reason, data)

def forecast_tool(data_points: str) -> str:
    """Forecast future values from a list"""
    try:
        # Remove quotes if present
        data_clean = data_points.strip("'\"")
        data = json.loads(data_clean)
        return SoilSensorTools.forecast_temperature(data)
    except Exception as e:
        return f"Invalid input: {str(e)}. Provide a JSON array like [16.5, 16.8, 17.0]"

def create_tools():
    """Create LangChain tools for the agent"""
    
    tools = [
        Tool(
            name="check_threshold",
            func=lambda x: check_threshold_tool(*x.strip("'\"").split(',')[0:3]) if ',' in x else "Use format: value,threshold,sensor_name",
            description="Check if a sensor value exceeds a threshold. Input format: value,threshold,sensor_name"
        ),
        Tool(
            name="send_email_alert",
            func=send_email_tool,
            description="Send an email alert with a reason. Input format: 'reason'"
        ),
        Tool(
            name="forecast_temperature",
            func=forecast_tool,
            description="Forecast future values. Input format: a JSON array like '[16.5, 16.8, 17.0]'"
        ),
        Tool(
            name="check_alert_cooldown",
            func=lambda x: SoilSensorTools.check_alert_cooldown(),
            description="Check when the last alert was sent"
        ),
    ]
    
    return tools


def load_sensor_data(json_path="../orin_soil_data.json"):
    """Load sensor data"""
    with open(json_path, 'r') as f:
        return json.load(f)


def extract_readings(data):
    """Extract sensor readings"""
    readings = []
    for entry in data:
        if 'sensor_data' in entry:
            readings.append({
                'timestamp': entry.get('timestamp', ''),
                **entry['sensor_data']
            })
    return readings


def initialize_llm(model_name: str = "llama3.2:3b", use_local: bool = True):
    """
    Initialize LLM - either local (Ollama) or OpenAI fallback
    
    Args:
        model_name: Model name (e.g., "llama3.2:3b" for Ollama, "gpt-3.5-turbo" for OpenAI)
        use_local: If True, try to use local Ollama LLM; if False or unavailable, use OpenAI
    """
    if use_local and OLLAMA_AVAILABLE:
        try:
            # Test if Ollama is running and model is available
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                
                if any(model_name in name for name in model_names):
                    print(f"Using local Ollama LLM: {model_name}")
                    return Ollama(
                        model=model_name,
                        base_url="http://localhost:11434",
                        temperature=0.1
                    )
                else:
                    print(f"Warning: Model {model_name} not found in Ollama. Available models: {model_names}")
                    print("Please run: ollama pull {model_name}")
            else:
                print("Warning: Cannot connect to Ollama. Is it running?")
                print("Start Ollama with: ollama serve")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")
            print("Falling back to OpenAI...")
    
    # Fallback to OpenAI
    print("Using OpenAI (cloud-based)")
    api_key = load_api_key()
    if not api_key:
        raise ValueError(
            f"OpenAI API key not found at {API_KEY_PATH}. "
            "Either set up Ollama for local inference or provide OpenAI API key."
        )
    
    return ChatOpenAI(
        api_key=api_key,
        model="gpt-3.5-turbo",
        temperature=0.1
    )


def main():
    """Run the agentic soil sensor monitor with local LLM"""
    
    print("Initializing the SPRIGBOT Soil Sensor Agent (Local LLM)...")
    
    # Load data
    data = load_sensor_data()
    readings = extract_readings(data)
    
    # Get latest reading
    latest = readings[-1]
    
    print(f"\nLatest Reading:")
    print(f"   Temperature: {latest['temp_SOIL']}°C")
    print(f"   Moisture: {latest['water_SOIL']}%")
    print(f"   Battery: {latest['Bat']}V")
    print(f"   Conductivity: {latest['conduct_SOIL']}")
    
    # Initialize LLM - try local first, fallback to OpenAI
    # Change model_name to match what you installed (e.g., "llama3.2:1b", "mistral:7b")
    llm = initialize_llm(model_name="llama3.2:3b", use_local=True)
    
    # Create tools
    tools = create_tools()
    
    # Create ReAct prompt template
    prompt = PromptTemplate.from_template("""
    You are a helpful assistant that can use tools to answer questions.
    
    {tools}
    
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Begin!
    
    Question: {input}
    Thought:{agent_scratchpad}""")
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    # Agent's task
    task = f"""
    You are monitoring IoT soil sensors. Analyze the latest reading and take appropriate action.
    
    Latest Reading:
    - Soil Moisture: {latest['water_SOIL']}% (Threshold: 5.0%)
    - Soil Temperature: {latest['temp_SOIL']}°C (Threshold: 25.0°C)
    - Battery: {latest['Bat']}V
    - Conductivity: {latest['conduct_SOIL']}
    
    Your objectives:
    1. Check if any values exceed thresholds
    2. If critical, send an alert (but check cooldown first)
    3. Analyze trends from recent readings if available
    4. Provide recommendations
    
    Take action autonomously. Don't just report - decide what to do and do it.
    """
    
    print("\n" + "="*60)
    print("AGENT TASK")
    print("="*60)
    print(task)
    print("="*60 + "\n")
    
    # Run agent
    result = agent_executor.invoke({"input": task})
    result_text = result['output']
    
    print("\n" + "="*60)
    print("AGENT COMPLETED")
    print("="*60)
    print(result_text)
    print("="*60 + "\n")
    
    # Show alert history
    if ALERT_STATE['alert_history']:
        print("\nAlert History:")
        for alert in ALERT_STATE['alert_history'][-5:]:  # Last 5
            print(f"   {alert['timestamp']}: {alert['sensor']} = {alert['value']} ({alert['status']})")


if __name__ == "__main__":
    main()

