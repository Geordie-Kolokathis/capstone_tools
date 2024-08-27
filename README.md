# capstone_tools
    Misc repo for software tools used by Cable Braiding smart sensor project

# sensor_data_logger.sh
    Writes sensor data and time measured, semicolon-separated, line by line to a .txt file.
    A new file is created every 100KB, where data will continue to be written.
    The file size before a new file is created should be tuned once the sensor read is implemented.
    At the moment, the script writes dummy data.
    Outputs data to sensor_logs directory

    Run locally:
    ./sensor_data_logger.sh

    Run via Docker:
    docker run -it -v "{absolute_path_to_repo}:/local_workspace" -w /local_workspace ubuntu:latest /bin/bash -c "./sensor_data_logger.sh" 

    Requires docker to be installed w/ local ubuntu container
    Can be exited via Ctrl+C
