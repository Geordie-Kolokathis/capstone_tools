import argparse
import os
from datetime import datetime
import matplotlib.pyplot as plt
import psycopg2

# Requires:
# pip install matplotlib
# pip install psycopg2

def convert_value(value):
    """
    Stub function to convert the value into more meaningful data.
    Currently, it just returns the integer representation of the input.
    Modify this function as needed to implement actual conversion logic.

    Consider input arg for different conversions based on sensor. Should
    return a distance value of some form.
    """
    return int(value)  # Placeholder conversion

def convert_timestamp(unix_timestamp):
    """
    Converts a Unix epoch timestamp in seconds to a readable date-time format.
    Returns the date-time string in the format YYYY-MM-DD-HH-mm-ss.
    """
    # Convert the Unix timestamp to a datetime object
    dt_object = datetime.fromtimestamp(float(unix_timestamp))
    # Format the datetime object into the desired string format
    return dt_object.strftime('%Y-%m-%d-%H-%M-%S')

def process_file(file_path):
    """
    Reads data from a file, processes each line to extract value and timestamp,
    converts them using respective functions, and stores the results in a list of tuples.
    """
    results = []

    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into value and timestamp
            value, timestamp = line.strip().split(';')

            # Convert the value using the value conversion function
            converted_value = convert_value(value)

            # Convert the timestamp using the timestamp conversion function
            converted_timestamp = convert_timestamp(timestamp)

            # Store the results as a tuple in the results list
            results.append((converted_value, converted_timestamp))

    return results

def process_directory(directory_path):
    """
    Processes all .txt files in the specified directory.
    Calls process_file on each .txt file found.
    """
    all_results = []

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a .txt file
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {file_path}")

            # Process the file and append the results
            file_results = process_file(file_path)
            all_results.extend(file_results)

    return all_results

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

def write_to_database(data, table_name):
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

        # Create table if it does not exist
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                value INTEGER,
                timestamp TIMESTAMP
            );
        """)

        # Insert data into the database
        for value, timestamp in data:
            cursor.execute(
                f"INSERT INTO {table_name} (value, timestamp) VALUES (%s, %s);",
                (value, datetime.strptime(timestamp, '%Y-%m-%d-%H-%M-%S'))
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
