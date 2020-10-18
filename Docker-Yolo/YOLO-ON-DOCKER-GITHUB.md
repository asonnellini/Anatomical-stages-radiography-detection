# Prepare the Images and the annotations for YOLO

1.  Annotate images with VGG Annotator -
    http://www.robots.ox.ac.uk/~vgg/software/via/

2.  Save the annotations in csv file
    
    1.  See example
        Docker-Yolo/VGGvsYolo-Annotations/VGGAnnotation-example.csv

3.  Run the script VGG-2-Yolo-annotations.ipynb to generate the:
    
    2.  \<imageId\>.txt file with YOLO Compatible annotations for
        \<imageId\>.png
        
        1.  See for
                example
            
            1.  Docker-Yolo/VGGvsYolo-Annotations/outPut-VGG-2-Yolo-annotations/
                1998\_AnteroPosterior\_supine.png
            
            2.  Docker-Yolo/VGGvsYolo-Annotations/outPut-VGG-2-Yolo-annotations/
                1998\_AnteroPosterior\_supine.txt
    
    3.  Generate a txt file that list the path (path within the Docker
        container) of for the
            images
        
        2.  Docker-Yolo/VGGvsYolo-Annotations/outPut-VGG-2-Yolo-annotations/
            1998\_AnteroPosterior\_supine.txt
        
        3.  Note: You will have to spit this text file to generate the
            train.txt and test.txt files, each of them with the list of
            images (and their path on the Docker image) for train and
            test respectively

4.  The above files will be later on uploaded on the EC2 where the
    docker image runs – see section 3

# Creation of the Docker image for YOLOV4

1.  Deploy an EC2 with the following setup:
    
      - EC2 Type: P2
    
      - AMI: Deep Learning Base AMI (Ubuntu 18.04) Version 30.0
    
      - IAM Role: Grant full access to S3 Buckets
    
      - Public IP: make sure to be able to SSH into the machine

2.  Install Docker
    
      - E.g. “quick-dirty” solution
    
      - \>\> curl -fsSL https://get.docker.com -o get-docker.sh
    
      - \>\> sudo sh get-docker.sh

3.  Create on the EC2 a folder:
    
      - Save in this folder the files and folders of
        Docker-Yolo/creation-yolo-image-P2 on this github
    
      - The content of the folder must be like below

![](.//media/image1.png)

  - Please check the content of Dockerfile to get acquainted about what
    operations will be performed by Docker when building the image

  - From this folder run (note the dot at the end of the command)
    
      - \>\> docker build -t \<container-name\> .

  - For example (note the dot at the end of the command)
    
      - \>\> docker build -t yolo-container .

  - The final result will be:

![](.//media/image2.png)

4.  Optionally you can tag your container and push it to your Docker
    repository
    
      - \>\> docker tag yolo-container
        \<docker-account-name\>/\<custom-image-name\>
    
      - \>\> docker login
        
          - Type your user and then the pwd
    
      - \>\> docker push \<docker-account-name\>/\<custom-image-name\>

# Run the Docker Image with Yolo

1.  Create an S3 bucket named //yolo-project/
    
      - Create a folder //yolo-project/setupToStartYolo/
    
      - Upload on the S3 the images and annotations produced after
        section 1:
        
          - A zip file that has
            
              - The images
            
              - For each image, the corresponding txt file with YOLO
                compatible annotations
        
          - The train.txt and test.txt files with the paths to the
            images
    
      - Eg. The structure on the S3 is going to be
        
        \\---yolo-project/setupToStartYolo/
        
        | test.txt (path images for test)
        
        | train.txt (path images for train)
        
        |
        
        \+---pic.zip
        
        | \\---image1.png
        
        | \\---image1.txt

2.  Deploy an EC2 with the following setup:
    
      - EC2 Type: P2
    
      - AMI: Deep Learning Base AMI (Ubuntu 18.04) Version 30.0
    
      - IAM Role: Grant full access to S3 Buckets this is needed to
        transfer files
    
      - Public IP: make sure to be able to SSH into the machine
    
      - Execute the User Data Script
        Docker-Yolo/ec2-User-Script-for-Yolo.sh
        
          - Note: we are assuming that a docker image with YOLO named is
            available in one Docker repository – the script refers
            specifically to the image asonnellini/yolo-custom-folders,
            you should change it to point it to the image of your
            interest
    
      - Once the script is executed:
        
          - You will finally have the following folders/files on the EC2

![](.//media/image3.png)

  - The docker image with YOLO will be available on the EC2

<!-- end list -->

  - Run the Docker image executing the following command:
    
      - \>\> sudo docker run -it --gpus all -v ~/exchange:/exchange
        asonnellini/yolo-custom-folders
        
          - Note the above command ensures the Docker Image can use all
            the gpus and that the folder ~/exchange on the EC2 is shared
            with the folder /exchange on the Docker Image

  - At this point in time:
    
      - You will be prompted inside the Docker Image
    
      - The setup shown below is in place

![](.//media/image4.png)

  - To ensure everything is fine you can try to run a test:
    
      - Download some weights for the coco.dataset:
        
          - \>\> wget
            https://github.com/AlexeyAB/darknet/releases/download/darknet\_yolo\_v3\_optimal/yolov4.weights
    
      - Run a test detection
        
          - \>\>\>\> ./darknet detector test ./cfg/coco.data
            ./cfg/yolov4.cfg ./yolov4.weights data/dog.jpg -thresh 0.25

# Train YOLO

From “inside” the Docker Image:

  - Adjust the parameters in yolo-obj.cfg file to match your needs (e.g.
    batch size, height and width)

  - Start a run executing for example the script
    /code/darknet/obj-config-files/Yolo-Train.sh:
    
      - \>\> /code/darknet/darknet detector train
        /code/darknet/obj-config-files/obj.data
        /code/darknet/cfg/yolo-obj.cfg /code/darknet/yolov4.conv.137
        -dont\_show -mjpeg\_port 8090 -map

  - During the training YOLO will dump in the folder /exchange/backup
    the weights every 100 iterations

  - You can check the GPU memory consumption running:
    
      - \>\> nvidia-smi

# Predict with YOLOs

From “inside” the Docker image:

  - Change in /code/darknet/cfg/yolo-obj.cfg:
    
      - Uncomment the part about testing (\#batch=1 \#subdivisions=1)
    
      - Comment the part about training (batch=64 subdivisions=16)

  - Run the below command – the output of the detection will be dumped
    in /exchange/result.txt
    
      - \>\> /code/darknet/darknet detector test
        /code/darknet/obj-config-files/obj.data
        /code/darknet/cfg/yolo-obj.cfg
        /exchange/backup/yolo-obj\_last.weights
        /exchange/images/9732\_AnteroPosterior\_unspecified.png -thresh
        0.25 -ext\_output \> /exchange/result.txt
