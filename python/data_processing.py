import argparse
import os
from datetime import datetime, time
import matplotlib.pyplot as plt
import psycopg2
import numpy as np
from scipy.signal import find_peaks

# Requires:
# pip install matplotlib
# pip install psycopg2
# pip install scipy

def convert_value(value):
    """
    Stub function to convert the value into more meaningful data.
    Currently, it just returns the integer representation of the input.
    Modify this function as needed to implement actual conversion logic.

    Consider input arg for different conversions based on sensor. Should
    return a distance value of some form.
    """
    return int(value)

def seconds_to_sql_time(seconds_str):
    seconds_float = float(seconds_str)
    # Extract hours, minutes, seconds, and microseconds
    hours = int(seconds_float // 3600) % 24
    minutes = int((seconds_float % 3600) // 60)
    seconds = int(seconds_float % 60)
    microseconds = int((seconds_float - int(seconds_float)) * 1_000_000)
    
    # Create a TIME object
    return time(hour=hours, minute=minutes, second=seconds, microsecond=microseconds)

def estimate_rolling_rpm(data_values, time_values, window_size, min_time_interval):
    rolling_rpm = []
    
    # Calculate the number of windows
    num_windows = len(data_values) // window_size

    # Iterate through each exclusive window
    for w in range(num_windows):
        # Get the current window of time and data values
        start_index = w * window_size
        end_index = start_index + window_size
        time_window = time_values[start_index:end_index]
        data_window = data_values[start_index:end_index]

        # Find peaks in the current window
        peaks, _ = find_peaks(data_window)

        # Filter peaks based on minimum time interval
        filtered_peaks = []
        last_peak_time = None

        for peak in peaks:
            if last_peak_time is None or (time_window[peak] - last_peak_time) >= min_time_interval:
                filtered_peaks.append(peak)
                last_peak_time = time_window[peak]

        if len(filtered_peaks) > 1:  # Need at least two peaks to compute an average period
            # Calculate the times of all filtered peaks
            peak_times = np.array(time_window)[filtered_peaks]
            # Calculate time differences between all consecutive peaks
            time_diffs = np.diff(peak_times)

            # Calculate the average period from the time differences
            average_period = np.mean(time_diffs)

            # Calculate RPM from the average period
            rpm = 60 / average_period

            # Append the RPM and the midpoint time of the window to the result
            midpoint_time = np.mean(peak_times)
            rolling_rpm.append((int(rpm), seconds_to_sql_time(midpoint_time)))

    return rolling_rpm

def process_file(file_path):
    """
    Reads data from a file, processes each line to extract value and timestamp,
    converts them using respective functions, and stores the results in a list of tuples.
    """
    distance = []
    rpm = []
    distance_raw = []
    time_raw = []

    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into value and timestamp
            timestamp, value = line.strip().split(';')

            # Convert the value using the value conversion function
            converted_value = convert_value(value)

            # Convert the timestamp using the timestamp conversion function
            converted_timestamp = seconds_to_sql_time(timestamp)

            # Store the results as a tuple in the results list
            distance.append((converted_value, converted_timestamp))
            distance_raw.append(int(value))
            time_raw.append(float(timestamp))

    # 175 data points used for rolling rpm - approx 4 seconds
    rpm = estimate_rolling_rpm(distance_raw, time_raw, 175, 0.5)

    return [distance, rpm]

def process_directory(directory_path):
    """
    Processes all .txt files in the specified directory.
    Calls process_file on each .txt file found.
    """
    distance_all = []
    rpm_all = []

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a .txt file
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {file_path}")

            # Process the file and append the results
            metrics = process_file(file_path)
            distance_all.extend(metrics[0])
            rpm_all.extend(metrics[1])

    return {'distance': distance_all, 'rpm': rpm_all}

def plot_data(data):
    """
    Plots the processed data as a dot plot with timestamp on the x-axis and
    converted value on the y-axis.
    """
    # Extract x (timestamps) and y (converted values) from the data
    x = [datetime.strptime(item[1], '%Y-%m-%d-%H-%M-%S') for item in data]
    y = [item[0] for item in data]

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.scatter(x, y, c='blue', marker='o', s=10)
    plt.xlabel('Timestamp')
    plt.ylabel('Converted Value')
    plt.title('Dot Plot of Converted Values Over Time')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def write_to_database(metrics, sensor_name):
    """
    Writes the processed data to a local PostgreSQL database.
    Each entry in the data list is expected to be a tuple (converted_value, converted_timestamp).
    """
    # Database connection parameters
    db_params = {
        'dbname': 'sensor_data',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432
    }

    # Establish a connection to the PostgreSQL database
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        for metric in ['distance', 'rpm']:
            # Create table if it does not exist
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {sensor_name}_{metric} (
                    id SERIAL PRIMARY KEY,
                    value INTEGER,
                    time TIME
                );
            """)

            # Insert data into the database
            for value, timestamp in metrics[metric]:
                cursor.execute(
                    f"INSERT INTO {sensor_name}_{metric} (value, time) VALUES (%s, %s);",
                    (value, timestamp)
                )

            # Commit the changes
            conn.commit()
            print("Data successfully written to the database.")

    except Exception as e:
        print(f"Error writing to the database: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def main():
    # Set up argument parsing for the input directory and additional flags
    parser = argparse.ArgumentParser(description='Process all .txt files in a directory with value;timestamp pairs.')
    parser.add_argument('--input_directory', type=str, help='Path to the directory containing .txt files')
    parser.add_argument('--plot', action='store_true', help='Flag to plot the processed data')
    parser.add_argument('--db', action='store_true', help='Flag to write the processed data to the database')
    parser.add_argument('--table_name', type=str, help='Name of database table to write data to')

    # Parse the command line arguments
    args = parser.parse_args()

    # Process the directory and retrieve all results
    all_processed_data = process_directory(args.input_directory)

    # Plot the data if the plot flag is specified
    if args.plot:
        plot_data(all_processed_data)

    # Write to the database if the db flag is specified
    if args.db:
        write_to_database(all_processed_data, args.table_name)

if __name__ == "__main__":
    main()
