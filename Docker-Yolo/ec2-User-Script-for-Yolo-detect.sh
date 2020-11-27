#!/bin/bash
# This script bootstraps the ec2 in such a way that, upon its execution the docker container with yolo and the flas api will be up and running with no need of manual intervention
# This script has been tested on an EC2 P2
sudo apt-get update
sudo apt-get install -y zip
sudo apt-get install -y awscli
sudo mkdir /home/ubuntu/dockerInstall
sudo curl -fsSL https://get.docker.com -o /home/ubuntu/dockerInstall/get-docker.sh
sudo sh /home/ubuntu/dockerInstall/get-docker.sh
# The directory exhchange will be shared with docker. 
# It will host the images and txt files to be used by yolo - see also the Dockerfile for more details 
sudo mkdir /home/ubuntu/exchange
# Back up directory will host the weights saved by yolo
sudo mkdir /home/ubuntu/exchange/backup
# images directory will host the images that yolo will train on
sudo mkdir /home/ubuntu/exchange/images
# Download the docker images for yolo training + flask
sudo docker pull asonnellini/yolo-custom-folders-flask_v2
# Start the docker image and run flask api
sudo docker run -d --rm -p 8090:8090 --gpus all -v ~/exchange:/exchange asonnellini/yolo-custom-folders-flask_v2 python3 darknet/flask-API/flask_api.py