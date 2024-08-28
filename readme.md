## Locations and Files
/notebooks contains several jupyter notebooks with data processing and model training. It might be easier to train in a different shell as the pandas package versions required for transformer training can clash with the packages required for the docker image that needs to run in the server environment. 

process_stream.py is the main script where the model is invoked on the frames of the videostream for detection. Detections are recorded in a csv file and the detection frames are stored in /docker_output. The script sends an email through SMTP to HVC members that are interested every day with the count of that day. 

process_stream_only.py is for local testing, which does not contain any email sending. 

in the .env file you can store environment variables such as the stream path and videotype. 


## Process
1. build the docker image with

`docker build -t <image-name> --platform=linux/amd64 .`

2. Test the working of the docker image / docker instructions with s

`docker compose up`

3. When everything looks good, save docker image to tar.gz file with 

`docker image save <image-name> | gzip > <filename>.tar.gz`

Then move this file to the HVC server in its own folder on the E:/ disk., adjust the docker compose file for any environment changes and run from the command prompt with docker compose up to start the application. 

4.  In the powershell of the server, run 
`docker load -i <filename>.tar.gz` 
to load the docker image. 

5. use `docker compose up (-d)` to run the docker image. check with `docker ps` and `logs` if it's running correctly.

* For easy changes, the docker-compose file mounts the python scripts, so that you can easily change things in this script without needing to build a new image. Simply do `docker compose down`, save your changes in the python scripts and run docker compose up again. 

