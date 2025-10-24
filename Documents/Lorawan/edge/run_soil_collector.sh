#!/bin/bash

# Soil Sensor Data Collector Runner
# This script runs the orin_soil_collector.py and logs the output

# Configuration
LOG_FILE="soil_collector.log"
PYTHON_SCRIPT="orin_soil_collector.py"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to script directory
cd "$SCRIPT_DIR" || {
    echo "$(date): ERROR - Could not change to directory $SCRIPT_DIR" >> "$LOG_FILE"
    exit 1
}

# Log start time
echo "$(date): Starting soil data collection..." >> "$LOG_FILE"

# Run the Python script and capture output
python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

# Check exit status
if [ $? -eq 0 ]; then
    echo "$(date): Soil data collection completed successfully" >> "$LOG_FILE"
else
    echo "$(date): ERROR - Soil data collection failed with exit code $?" >> "$LOG_FILE"
fi

# Log end time
echo "$(date): Soil data collection finished" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
