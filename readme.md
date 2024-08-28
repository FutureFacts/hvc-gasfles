## Locations and Files

## Process
1. build the docker image with

`docker build -t <image-name> --platform=linux/amd64 .`

2. Test the working of the docker image / docker instructions with s

`docker compose up`

3. When everything looks good, save docker image to tar.gz file with 

`docker image save <image-name> | gzip > <filename>.tar.gz`

Then move this file to the HVC server in its own folder on the E:/ disk., adjust the docker compose file for any environment changes and run from the command prompt with docker compose up to start the application. 


docker load -i trainset4.tar.gz
chmod 744 24-03-23-20m-22m_video.mp4