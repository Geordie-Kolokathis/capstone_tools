#!/bin/bash

# Directory to store log files
LOG_DIR="sensor_logs"
mkdir -p $LOG_DIR

# Setup python venv and install packages
python -m venv venv
source venv/bin/activate

pip install adafruit-circuitpython-apds9960
pip install board

# Read sensor data and echo with date timestamp
read_sensor_data() {
    PROX_DATA=$(python python/read_proximity.py)
    echo "${PROX_DATA};$(date)"
}

# Function to handle cleanup on exit
cleanup() {
    echo "Exiting script..."
    echo "Output sensor data to '${LOG_DIR}'".
    exit 0
}

# Trap Ctrl+C (SIGINT) to run cleanup function
trap cleanup SIGINT

# Infinite loop to read sensor data continuously
while true; do
    # Create a new log file with timestamp
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    LOG_FILE="$LOG_DIR/$TIMESTAMP.txt"
    
    # Write sensor data to log file
    echo "Starting new log file: $LOG_FILE"
    while true; do
        # Read sensor data
        SENSOR_DATA=$(read_sensor_data)
        
        # Append data to the current log file
        echo $SENSOR_DATA >> $LOG_FILE
        
        # Create a new file every 100 KB (102400 bytes) - ~2845 lines 
        # Adjust based on desired file size & read time
        FILE_SIZE=$(stat -c%s "$LOG_FILE")
        if [ $FILE_SIZE -ge 102400 ]; then
            break
        fi
    done
done
