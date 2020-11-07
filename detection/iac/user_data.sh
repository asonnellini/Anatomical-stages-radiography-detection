#!/bin/bash
# This script bootstraps the ec2 in such a way almost everything is setup to start a new yolo run on docker
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
# Download within the folder exchange from S3 yolo-project bucket the zipped images&txt files for yolo
sudo aws s3 sync s3://deep-yolo-project/setupToStartYolo/ /home/ubuntu/exchange
sudo unzip $(ls /home/ubuntu/exchange/*zip) -d /home/ubuntu/exchange/images/
# Give permissions to all users on all directories and files in the exchange folder
sudo chmod -R 777 /home/ubuntu/exchange/

# get yolo-and-flask config files from s3
# !> consider get it from github repository when it will be made public
sudo aws s3 cp s3://deep-config/yolo-and-flask/keyboard
sudo mkdir darknet
sudo aws s3 sync s3://deep-config/yolo-and-flask/darknet ./darknet
# get the dockerfile and build the docker image
# !> consider get it from a github repository
sudo mkdir dockerfile
sudo aws s3 cp s3://deep-config/yolo-and-flask/dockerfile ./dockerfile/
# Build a docker image with the name 
sudo docker build -t yolo-app dockerfile/.
# run the docker image
# sudo docker run -it -p 8090:8090 --gpus all -v ~/exchange:/exchange -it yolo-app

sudo docker run -d --rm -p 8090:8090 --gpus all -v ~/exchange:/exchange yolo-app python3 darknet/flask-API/flask_api.py

##################################################################################################################
#sudo touch /home/ubuntu/run-Yolo-Docker.sh
# Create the script to run the docker image loading the folder "exchange" as a volume on the container
#echo "sudo docker run -it -p 8090:8090 --gpus all -v ~/exchange:/exchange asonnellini/yolo-custom-folders" >> /home/ubuntu/run-Yolo-Docker.sh
#sudo chmod +x /home/ubuntu/run-Yolo-Docker.sh
# Download the docker images for yolo training
#sudo docker pull asonnellini/yolo-custom-folders
# Download the docker images for yolo training + flask
#sudo docker pull asonnellini/yolo-custom-folders-flask