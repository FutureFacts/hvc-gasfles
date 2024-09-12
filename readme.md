# Gasflessencilinder telling HVC
This project contains the code for the application to detect and count the gasflessen in a videostream of a slakkenband. It uses a Vision Transformer trained on a custom dataset of frames of the videostream. It also has an automated smtp setup so that the counts and timestamps of the detected gasflessen are reported to the end user. 

#Usage


## Locations and Files
- _/notebooks_ contains several jupyter notebooks with data processing and model training.

 *It might be easier to train in a different shell than the rest of the project, since the pandas package version required for transformer training can clash with the packages required for the docker image that needs to run in the server environment.

After getting the performance you want on the testset with your model, you can use the checkpoint of the model for inference on the videostream with the scripts below and store it in _/models_

- _process_stream.py_ is the main script where the model is invoked on the frames of the videostream for detection. Detections are recorded in a csv file and the detection frames are stored in /docker_output. The script sends an email through SMTP to HVC members that are interested every day with the count of that day. 

- _process_stream_only.py_ is for local testing, which does not contain any email sending. 

in the .env file you can store environment variables such as the stream path and videotype. 


## Process of deployment on HVC server
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


## Contributors
Max Druyvesteyn (some help from Niels Backer)
