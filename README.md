# capstone_tools
    Misc repo for software tools used by Cable Braiding smart sensor project

# sensor_data_logger.sh
    Writes sensor data and time measured, semicolon-separated, line by line to a .txt file.
    A new file is created every 100KB, where data will continue to be written.
    The file size before a new file is created should be tuned once the sensor read is implemented.
    At the moment, the script writes dummy data.
    Outputs data to sensor_logs directory

    Run locally:
    ./sensor_data_logger.sh.
    - Requires the dependencies listed in docker/Dockerfile installed locally to function.

    Run via Docker:
    - Either build and tag the dockerfile at docker/Dockerfile, or use a container with the same dependencies installed. To build:
    1. cd docker
    2. docker build .
    3. docker tag {hash} ubuntu:{version}
        - Find {hash} using 'docker images'.
        - Set {version} to whatever you like.
    4. docker run -it -v "{absolute_path_to_repo}:/local_workspace" -w /local_workspace ubuntu:{version} /bin/bash -c "./sensor_data_logger.sh" 

    Requires docker to be installed w/ local ubuntu container. May have issues with accessing physical sensors when run by docker container, this use case is untested. Docker mostly considered for use as a tool where the physical board isn't available.

    Can be exited via Ctrl+C
