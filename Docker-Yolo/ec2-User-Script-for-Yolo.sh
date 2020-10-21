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
# images directory will host the weights saved by yolo
sudo mkdir /home/ubuntu/exchange/images
# Download within the folder exchange from S3 yolo-project bucket the zipped images&txt files for yolo
sudo aws s3 sync s3://yolo-project/setupToStartYolo/ /home/ubuntu/exchange
sudo unzip $(ls /home/ubuntu/exchange/*zip) -d /home/ubuntu/exchange/images/
# Give permissions to all users on all directories and files in the exchange folder
sudo chmod -R 777 /home/ubuntu/exchange/
sudo touch /home/ubuntu/run-Yolo-Docker.sh
# Create the script to run the docker image loading the folder "exchange" as a volume on the container
echo "sudo docker run -it -v ~/exchange:/exchange asonnellini/yolo-custom-folders" >> /home/ubuntu/run-Yolo-Docker.sh
sudo chmod +x /home/ubuntu/run-Yolo-Docker.sh
# Download the docker images for yolo
sudo docker pull asonnellini/yolo-custom-folders