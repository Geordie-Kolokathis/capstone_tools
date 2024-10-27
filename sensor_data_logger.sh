#!/bin/bash

# Default values for plot and db flags
PLOT_FLAG=""
DB_FLAG=""
SENSOR_NAME=""

# ./script.sh --sensor_name temperature /path/to/output --plot --db

# Parse input parameters
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --plot) PLOT_FLAG="--plot" ;;       # Add the --plot flag if specified
        --db) DB_FLAG="--db" ;;             # Add the --db flag if specified
        --sensor_name) SENSOR_NAME="$2"; shift ;;  # Capture the sensor name
        *) OUTPUT_DIR="$1" ;;               # Assume the first argument is the output directory
    esac
    shift
done

# Setup python venv and install packages
python3 -m venv venv
source venv/bin/activate

# Sensor reading packages
pip install adafruit-circuitpython-apds9960
pip install adafruit-blinka
# Data processing packages
pip install matplotlib
pip install psycopg2
pip install scipy
pip install numpy

OUTPUT_DIR='sensor_logs'

python3 "python/${SENSOR_NAME}_read.py" --output_dir $OUTPUT_DIR

# Function to handle cleanup on exit
cleanup() {
    echo "Exiting Sensor Read script..."
    python3 python/data_processing.py --input_directory $OUTPUT_DIR $PLOT_FLAG $DB_FLAG --table_name $SENSOR_NAME
    exit 0
}

# Trap Ctrl+C (SIGINT) to run cleanup function
trap cleanup SIGINT
