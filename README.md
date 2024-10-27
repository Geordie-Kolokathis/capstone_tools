# capstone_tools
    Misc repo for software tools used by Cable Braiding smart sensor project

# sensor_data_logger.sh
    Writes sensor data and time measured, semicolon-separated, line by line to a .txt file.
    Takes input args which specify the sensor to measure from and whether or not to write to DB
    Writes data to sensor_logs dir, and triggers data processing upon Ctrl+C cancellation of the sensor reading.

    Run locally:
    ./sensor_data_logger.sh. <args>
    - Requires the dependencies listed in docker/Dockerfile installed locally to function. Pip packages installed in venv

    Run via Docker:
    - Either build and tag the dockerfile at docker/Dockerfile, or use a container with the same dependencies installed. To build:
    1. cd docker
    2. docker build .
    3. docker tag {hash} ubuntu:{version}
        - Find {hash} using 'docker images'.
        - Set {version} to whatever you like.
    4. docker run -it -v "{absolute_path_to_repo}:/local_workspace" -w /local_workspace ubuntu:{version} /bin/bash -c "./sensor_data_logger.sh" 

    Requires docker to be installed w/ local ubuntu container. May have issues with accessing physical sensors when run by docker container, this use case is untested. Docker mostly considered for use as a testing tool where the physical board isn't available.

    Can be exited via Ctrl+C during data processing, although not recommended if writing to DB.

# Database
    Database is being set up according to https://www.microfocus.com/documentation/idol/IDOL_12_0/MediaServer/Guides/html/English/Content/Getting_Started/Configure/_TRN_Set_up_PostgreSQL.htm

    Server listening port 5432, user: postgres, pw: password. Local DB only.

    CREATE DATABASE sensor_data WITH ENCODING 'UTF8'

# Dashboard
    Grafana, set up dashboard according to https://grafana.com/grafana/download?pg=get&plcmt=selfmanaged-box1-cta1
    
    Run server and connect via localhost, configured to read from the set up database.