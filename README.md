# Overview

This repository hosts the code of **Deep to the Bones,** an Application
that automatically detects anatomical sections of the body in
radiographies.

The application is a POC but shows already the feasibility of such a
system.

The drivers for this project, its detailed implementation, potential
improvements, past and currently standing issues are all documented.
This README file is the entry point to access all the relevant
documentation.

# Table of contents of the README

  - [Quick Start and highlights of the application](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master#quick-start-and-highlights-of-the-application)

  - [CONTEXT: WHY automatic detection of anatomical sections](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master#context-why-automatic-detection-of-anatomical-sections-in-radiographies-is-relevant)

  - [SOLUTION: WHAT can be done to minimize and precisely measure the absorbed dose](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master#solution-what-can-be-done-to-minimize-and-precisely-measure-the-absorbed-dose)

  - [IMPLEMENTATION: HOW to implement such a system](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master#implementation-how-to-implement-such-a-system)

  - [Examples of detections](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master#examples-of-detections)

  - [Possible improvements](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master#planned-improvements)

  - [Issues experienced and their resolution](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master#issues-experienced-and-their-resolution)

# Quick Start and highlights of the application

The user can easily use the application following the below procedure:

  - Open a browser and go [to this link](http://18.188.16.8:5000/) (the
    application might not be available or not performing the detection
    in case we stopped the EC2 that performs the detection)

  - Upload a radiography image (accepted formats so far are jpg, jpeg,
    png – dicom will be supported shortly)

  - Click on the ***Run Detection*** button

  - Click on ***Download the image*** below the image to download it

![](.//media/image1.png)

Main features of the application:

  - **Web-Based front-end** hosted on an EC2

  - Images saved on **Private s3** buckets to ensure high-reliability,
    availability, and security

  - **Detection performed by a YOLO v.4** **Neural Network** trained
    specifically for object detection of anatomical sections in
    radiographies

  - **Back-end**
    
      - Made of the a YOLO v.4 Neural Network running on a **Docker
        container hosted on a P2.xlarge EC2 – this increases the
        scalability of the back-end and the “portability” of YOLO v.4**
    
      - Equipped with a **FLASK RESTful API** **that enables easy
        integration with any front-end**

  - The detection is currently available for the following
sections:
    
      - Head
    
      - Spine
    
      - Chest
    
      - Abdomen
    
      - Pelvis

# CONTEXT: WHY automatic detection of anatomical sections in radiographies is relevant

“Radiology is the medical discipline that uses medical imaging to
diagnose and treat diseases within the bodies of animals, including
humans” - [Wikipedia](https://en.wikipedia.org/wiki/Radiology).

Radiographies and Computer Tomographies (CTs) have led to huge
improvements in the quality of medical diagnosis and treatments, almost
eliminating the need for dangerous exploratory surgery and other
invasive procedures.

![](.//media/image2.png)

On the other hand, these technologies make use of radiations which might
seriously harm patients’ health in case of excessive exposure, for
example increasing the probability to suffer from cancer.

The risks associated to exposure to medical radiation are difficult to
be quantified given that damages caused by radiations occur typically
many years after the exposure. Nevertheless, due to the wide adoption of
these technologies (Over 80 million CT scans performed in the US each
year, with prices ranging from 300 up to 5,000 $ - [see
www.americanhealthimaging.com](https://www.americanhealthimaging.com/how-much-does-a-ct-scan-cost/#:~:text=In%20general%2C%20you%20can%20expect,or%20bill%20your%20insurance%20provider.)),
this topic is crucial for all the actors of the public health: patients,
medical community, legislators, and Healthcare Industry.

In response to this need, legislators and the medical community have
defined protocols and procedures, while machines for radiographies and
CT have been equipped with more and more sophisticated tools to measure
and minimize the dose of radiation absorbed by the patient.

The topic of overexposure to radiation is particularly relevant for CTs.
Indeed, as shown in the below table from the article [Radiation Risk
from Medical
Image](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2996147/), CTs
expose patients up to 25 times more radiation doses than a standard
radiography.

![](.//media/image3.png)

It is also important to remark that the above figures are benchmarks
referring to “nominal condition of usage” of CT scans. In case of
misusage of the CT, the real dose absorbed by the patient can be higher.

As reported by a [whitepaper from
Philips](https://www.philips.it/c-dam/b2bhc/master/clinical-solutions/dosewise-solution-page/TheimportanceofpatientcenteringonCTradiationdoseoptimization.pdf),
modern CT scans can automatically optimize the intensity of the
radiation sent to the patient in order to minimize it without decreasing
the quality of the image. This tuning is performed by the automatic
exposure control (AEC) system and relies on a preliminary Radiography
scan of the patient that is take to allow the AEC to infers the optimal
intensity. These preliminary radiography scans are the so-called “scout
images”. Scout images are used by the AEC under the assumption that the
patient is well positioned in the CT Scan. Of course, in general this
might not be the case. CT technicians can apply the below procedure to
address this issue:

1)  Place the patient in the CT scan and perform a preliminary scout
    image of the patient – based on this image, the CT technician
    assesses the position of the patient and adjusts it

2)  A second scout image should then be performed to re-run the AEC and
    ensure its tuning is correct

3)  Eventually the CT Technician can select on the screen (which shows
    the last scout scan) the area of the patient to be scanned

Unfortunately, studies have shown that often the above procedure is not
applied, causing patients to be mis-positioned or the AEC not to be
tuned, or both. This has a double negative impact, as shown in the
figure and table below:

1)  Over-exposure/incorrect exposure of the patient to radiations

2)  Noisy images

![](.//media/image4.png)

![](.//media/image5.png)

As explained above, correctly placing a patient on the CT Scan ensures
the patient will receive the lowest possible dose of radiation. It is
important at the same time to precisely measure the amount of radiation
each section of the body absorbed. For this purpose, it is key to know
where each part of the body is located compared to the CT scan so that
the area of the section in object can be extracted and the absorbed dose
can be
computed.

# SOLUTION: WHAT can be done to minimize and precisely measure the absorbed dose

The issues described above can be solved implementing a system that is
capable of:

  - **Identifying the location of the patient and anatomical sections in
    the CT scan from the scout image**

  - **Measuring the misalignment of the patient compared to the CT scan
    and identify the corrections to be applied**; referring to the image
    below indeed, if the “physical” coordinates of the bounding box
    around the anatomical section (represented by an ellipsis) are
    known, then the distance between the middle of the section and the
    isocenter can be inferred from the distance between the isocenter
    and one edge of the bounding box

![](.//media/image6.png)

  - **Measuring from the scout image the area of each anatomical section
    to measure the dose it absorbed**; the picture below shows the view
    from a real Dose-Measure Solution from a major Healthcare vendor
    where anatomical sections are contoured to measure the absorbed
    dose; sections seems not to be precisely identified, for example the
    chest occupies a very narrow area while shoulders area is too wide –
    **we can do better than that\!**

![](.//media/image7.png)

# IMPLEMENTATION: HOW to implement such a system

The goals listed in the previous section can be implemented according to
the following high-level schema implementation:

  - **Identifying the location of the patient and anatomical sections in
    the CT scan from the scout image**
    
      - Take the radiography scout image
    
      - Run an object detection algorithm that identifies bounding boxes
        around each section
        
          - In this work we focused on the sections: HEAD, SPINE, CHEST,
            ABDOMEN, PELVIS
    
      - Extract the coordinates of the pixels on the image corresponding
        to the edges of the bounding boxes of anatomical sections
    
      - Convert those pixel coordinates in physical coordinate of the
        anatomical sections in the reference system of the CT

  - **Measuring the misalignment of the patient compared to the CT scan
    and identify the corrections to be applied**
    
      - Based on the above physical coordinates, measure the
        misalignment between the patient position and the correct
        position on the CT

  - **Measuring from the scout image the area of each anatomical section
    to measure the dose it absorbed**
    
      - We understand that the absorbed dose is measured approximating
        each anatomical section with an ellipsis – the area of the
        ellipsis can be measured based on the length of the axis of the
        ellipsis and the axis of the ellipsis have the same length of
        the sides of the bounding boxes

## Detailed implementation

In this section we will provide more details about how we built the
whole application, starting from the choice of the object detection
model up to the target architecture.

### Object detection model – Why YOLO v.4

Our application uses YOLO v.4 as model to perform the detection.

We used the YOLO v.4 implementation in C++ using the darknet framework,
and publicly available [on this
github](https://github.com/AlexeyAB/darknet).

We chose a YOLO-like model because, [as described in the original YOLO
paper](https://arxiv.org/abs/1506.02640), it is capable to take into
account the whole image when performing the object detection (i.e. it
captures contextual information reducing for example the chance to
wrongly detect patches from the background) and generalize well. This
last property is quite relevant for our radiographies which were quite
different from each other both in terms of content and quality. YOLO is
also famous for being very fast in the detection phase (useful for real
time detection in videos) but this was not the most relevant property
within the context of our project.

[As described by the paper supporting
it](https://arxiv.org/abs/2004.10934), YOLO v.4 in particular is more
performant than previous versions in terms of accuracy, and is optimized
to run on “standard/common” GPUs, i.e. without the need to have monster
GPUs.

We did not consider at all YOLO v.5 given that it is not supported by
any scientific paper or documentation that can prove the quality of this
model. It is indeed quite debatable whether it is appropriate to call it
YOLO v.5 or not.

### Dataset

The Dataset we used to train Yolo is characterized by the following:

  - **Original dataset**: [IRMA X-Ray Kaggle
    dataset](https://www.kaggle.com/raddar/irma-xray-dataset)

  - **Content of the image**: the original dataset contains
    approximately 14,000 X-rays of various human body parts. Images are
    scans of old paper X-rays and do not meet current digital X-ray
    standards, hence their quality is not good.
    
    Nevertheless, this dataset has radiographies from any section of the
    body, not “just” radiographies of the chest which are the most
    common to find.

  - **Number of images** effectively used to train and test the
    Application: 939 images, splitted in train (75%) and test set (25%)
    – all of them were manually annonated

  - **Image file format**: PNG – we plan to support Dicom shortly

  - **Dataset preprocessing and annotations:** given the
    non-standardized nature of the images of our dataset, we had to
    manually review all the 14,000 images, select the ones with the
    Anatomical Sections of our interest and in some cases crop the
    borders of the images that had the typical “distortions” of an image
    that is manually scanned.
    
    Eventually we manually annotated all the selected images [using
    VGG](http://www.robots.ox.ac.uk/~vgg/software/via/) annotator, and
    convert the annotations to Yolo compatible format – [see the
    relevant documentation at this
    link](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master/Docker-Yolo#prepare-the-images-and-the-annotations-for-yolo)

### Training

Highlights of the training of Yolo:

  - Train performed on an EC2 P2.xlarge equipped with GPU Tesla K80 (11
    GB)

  - Duration of the training 36 hours

  - Number of iterations executed: 8700

  - Heigh/width of the image for the input layer: 256 (we had to lower
    it from the initial 416 to speed up the training)

  - Batch size: 160

  - Subdivision: 16

The image below shows the shape of the loss function after 3300
iterations – the first part of the plot is not available because during
the training the P2 instance was terminated by AWS causing the loss of
the plot.

![](.//media/image8.png)

### Architecture

The below schema shows the Architecture of our App and the flow of
events that take place once the User clicks on the Run Detection button.

![](.//media/image9.png)

The front-end:

  - Is an HTML page ( [home.html](https://github.com/asonnellini/Anatomical-stages-radiography-detection/blob/master/Frontend/home.html) ) hosted on an EC2 t2.micro

  - The same EC2 hosts a Flask API (see the file [app.py](https://github.com/asonnellini/Anatomical-stages-radiography-detection/blob/master/Frontend/app.py) ) that is
    connected to the HTML:
    
      - The HTML page makes post calls to the Front-End Flask API
        triggering the actions shown in the above diagram

The back-end:

  - **Is a P2xlarge EC2**

  - Hosts a **Docker container with YOLO v.4** and its trained weights - regarding the implementation of the docker image with Yolo please refer to [the specific README](https://github.com/asonnellini/Anatomical-stages-radiography-detection/tree/master/Docker-Yolo)

  - The Docker container has a **flask API** with an endpoint that triggers
    the detection

Back-end and front-end communicate with each other via a Lambda function
that ensures the compatibility of the calls from the front-end to the
back-end.

The above architecture allows to:

  - **Decouple the front-end from the back-end**
    
      - This allowed us to work almost independently on the front-end
        and the back-end without having integration problems

  - **Easily generate a presigned URL from the S3 bucket**

  - **Pave the way toward a more sophisticated and “production-ready”
    environment** like the one exposed in section Planned Improvements

# Examples of detections

In this section we show some of the detections performed by our App.
**None of these images were part of the training set.**

![](.//media/image10.jpeg)

![](.//media/image11.jpeg)

![](.//media/image12.jpeg)

![](.//media/image13.jpeg)

# Planned Improvements

This section describes improvements that we are planning to put in place
to enhance the current POC.

## Detection

1)  Use **more and higher quality images** to train the detection system

2)  Apply **Data Augmentation** to the training set

3)  **Use DICOM image format** to take advantage of their metadata as
    well, for example to **extrapolate from the coordinate of the
    bounding boxes on the image the physical coordinates of the patient
    anatomical sections** in the reference system of the CT – this will
    be relevant to correctly position the patient on the CT scan, like
    shown in the figure below and explained in the previous sections

![](.//media/image6.png)

4)  **Additional post-processing logic:** We can implement an
    a-posteriori logic to identify the diaphragm as the section of the
    body obtained by the intersection, as shown by the red box in the
    image below

![](.//media/image14.png)

## Architecture

5)  Improve the UX of the front-end

6)  Improve the architecture introducing a GTW API that decouples the
    front-end from the backend

![](.//media/image15.png)

**Important:** It is important to remark that the improvements 6 and 7
would allow to:

  - **Further decouple the front-end from the back-end**:
    
      - Any already existing solutions can integrate the back-end of our
        application just implementing a simple logic to communicate with
        the AWS API GTW
    
      - The front-end and the back-end will only communicate with the
        API GTW, so changes done on one “side” of the application will
        not directly impact the other “side”

  - **Increase the Scalability of the solution** to manage high number
    of requests

# Issues experienced and their resolution

This section describes the main issues we faced when building the POC.

  - **Issue:** Unable to install on a standard laptop all the
    dependencies needed to train YOLO V.4, mainly due to issues with
    disk space (particularly when compiling OpenCV)
    
      - **Resolution:** Build a docker image with Yolo in it

  - **Issue**: Unable to build the Docker image to host the YOLO NN when
    enabling the support for GPU
    
      - **Resolution**:
        
          - Use an EC2 equipped with:
            
              - GPU (e.g. P2)
            
              - AMI: ami-01bd6a1621a6968d7, i.e. Deep Learning AMI
                (UBUNTU 18.04) Version 36.0
            
              - Both the above are needed

  - **Issue:** We used P2.xlarge EC2 instances to train YOLO v.4,
    P2.xlarge are the cheapest P-type EC2 instances, equipped with GPU.
    Given the cost of on-demand instances (more than 1 $ per hour) and
    the fact that the training may last more than 2 days, we used Spot
    instances (0.27 dollars per hour). However, Spot instances can be
    terminated by AWS with no notice, causing the loss of the weights
    trained so far.
    
      - **Resolution:** When creating the EC2, ensure to disable the
        flag “delete on termination” for the volume of the EC2, so that
        even if the EC2 is terminated, the weights are not lost.

  - **Issue:** Calls to the flask API running on the docker container
    seems not to hit the flask API itself, even though the docker
    container is run with the flag ``` -p 8090:8090 ```
    
      - **Resolution:** change the flask\_api.py from:
        
          - ``` if \_\_name\_\_ == '\_\_main\_\_' :
            
            app.run(debug = True) 
            ```
            
            TO:
        
          - ``` if \_\_name\_\_ == '\_\_main\_\_' :
            
            app.run(host = '0.0.0.0', port = 8090, debug = True) ```

  - **Issue**: Unable to create and upload objects from an EC2 belonging
    to account A to a non-public S3 bucket that belongs to account B
    
      - **Resolution**:
        
          - Setup an IAM role for the EC2 on account A such that grants
            access to S3 buckets, for example:
            
              - ```
                
                {
                
                "Version": "2012-10-17",
                
                "Statement": \[
                
                {
                
                "Effect": "Allow",
                
                "Action": "s3:\*",
                
                "Resource": " \\\< ARN code of the S3 bucket \\\> "
                
                }
                
                \]
                
                }
                
                ```
        
          - Setup a policy on the bucket of account B to allow the role
            from account A to access and operate on the bucket
        
          - ```
            
            {
            
            "Version": "2012-10-17",
            
            "Statement": \[
            
            {
            
            "Effect": "Allow",
            
            "Principal": {
            
            "AWS": ""\<ARN code of the EC2 IAM role to access an S3
            bucket\>"
            
            },
            
            "Action": "s3:\*",
            
            "Resource": "\<ARN code of your S3 bucket\>/\*"
            
            }
            
            \]
            
            }
            
            ```

  - **Issue:** Unable to create a “working” presigned URL using a Lambda
    function of the account B for an object uploaded to an S3 bucket
    belonging to account B from an EC2 belonging to account A.
    
      - **Resolution**:
        
          - upload objects setting the flag 'ACL' =
            'bucket-owner-full-control', e.g.:
            
              - ``` s3\_client = boto3.client('s3')
            
              - s3\_client.upload\_file(fileToUpload, bucketName,
                object\_name,
                ExtraArgs={'ACL':'bucket-owner-full-control'}) ```
        
          - Set the bucket policy:
            
              - ```
                
                {
                
                "Version": "2012-10-17",
                
                "Statement": \[
                
                {
                
                "Effect": "Allow",
                
                "Principal": {
                
                "AWS": \[
                
                "arn:aws:iam::090887179158:role/s3\_access\_from\_EC2",
                
                "arn:aws:iam::794308064805:role/S3Role"
                
                \]
                
                },
                
                "Action": \[
                
                "s3:GetObject",
                
                "s3:PutObject",
                
                "s3:PutObjectAcl"
                
                \],
                
                "Resource": "arn:aws:s3:::my-YOLO/\*"
                
                }
                
                \]
                
                }
                
                ```

  - **Issue**: If we trigger a detection using the original darknet.py
    and darknet\_image.py files from the official github repository, the
    output image does not have the original shape. It has indeed the
    shape that is set in the yolo-obj-detect.cfg (416x 416 in our case)
    and the coordinates of the bounding boxes are expressed in
    “absolute” (i.e. not relative) value referring to the resized
    image. This is due to the fact that to perform the detection, the
    image has to be resized; unfortunately, in the original darknet.py
    and darknet\_image.py there was no mechanism to re-convert
    everything to the original size.
    
      - **Resolution**: we built the functions in the script detect2.py:
        
          - draw\_boxes\_original\_img(detections, image, colors)
        
          - detectImg(ImgInput, ImgOutput)

  - **Issue**: when starting the docker container along with the flask
    api from the below command line
    
    ``` sudo docker run -d --rm -p 8090:8090 --gpus all -v
    ~/exchange:/exchange asonnellini/yolo-custom-folders-flask\_v2
    python3 darknet/flask-API/flask\_api.py ```
    
    We received an error related to missing libdarknet.so even though
    this library was already in the folder darknet/flask-API/
    
      - **Resolution**: the error is due to the fact that the working
        dir for the container is /code. This is indeed what is set in
        the dockerfile via ``` WORKDIR /code ``` .
        
        Consequently when running the container from command line,
        docker looks for the library libdarknet.so in the working dir,
        i.e. /code.
        
        To resolve the issue we added the following line to the docker
        file
        
        RUN cp /code/darknet/libdarknet.so /code/

  - **Issue:** The presigned url that were generated from an EC2 were
    not working, meaning that when used an error referring to an invalid
    authentication method was raised.
    
      - **Resolution:** to solve the issue we generated URL using a
        Lambda function. We suspect the issue was due to the fact that
        the key were generated by an EC2 running on US, while they were
        used by European users. We believe that the authentication
        mechanism used for US users is not compatible with the one for
        European users. We did not have the chance to check it

  - **Issue**: Unable to upload and download images from a private S3
    bucket using a web front-end that communicates with an AWS API GTW +
    Lambda function to obtain pre-signed URL.  
    Every time we send from the web front-end a POST or GET call to the
    API GTW, we get errors related to CORS policies.
    
    If we do the same from Postman everything works fine.
    
      - **Resolution**: This issue is still outstanding and is what is
        currently preventing us from being able to upgrade the
        architecture to the one described in the Section Planned
        Improvement
