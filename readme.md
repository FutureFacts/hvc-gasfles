# Gasflessen detectie

This repo contains the code to detect gasfles cilinders in a video stream, based on a Visual Transformer model that classifies frames into whether or not they contain the gasfles. You can deploy the code in a docker image, or run it locally.

## Model
/notebooks contains jupyter notebooks showing the training process and model selection. The current model was obtained with the open source model from hugging face.

## Docker
In the dockerfile the requirements are installed through poetry. 
The docker-compose file ensures mounting and some environment variables can be set here (such as the video stream)

- Build docker image: `docker build -t /imagename/ .`
If you are planning to deploy on the hvc server, it's important to add  `--platform=linux/amd64`
- When your image is built, you can use `docker compose up` to run the app. 

-(optional) 
## Local
Set your environment variables in your local .env file.

Run
`python process_stream.py`


