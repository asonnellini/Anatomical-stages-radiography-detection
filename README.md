# Anatomical Stages Radiography Detection

[![gitlab-ci](https://gitlab.com/bngom/Anatomical-stages-radiography-detection/badges/uat/pipeline.svg)](https://gitlab.com/bngom/Anatomical-stages-radiography-detection)

A RESTFull API using **YOLO** to detect anatomical stages (head, chest, pelvis and spine) of radiograghy.

**Tags**:

- AWS: S3, EC2, API Gateway, Step functions, Lambda.
- IAC: Terraform.
- Hosting: Heroku
- Continious testing, continious delivery: gitlab-ci
- Bootstrapped with: Python, Node.js, React. 


![architecture.PNG](./img/architecture.PNG)

# Usage

```
git clone https://github.com/asonnellini/Anatomical-stages-radiography-detection.git
```

## Deploy Yolo on AWS EC2 Instance

We use Infrastructure as Code approach to deploy yolo on AWS EC2/P2 instance.

In the following we automatically:

- Provision the instance
- Install docker on the instance
- Deploy a containter with yolo
- In that container deploy a REST API to perform anatomical stage radiography detection on request.
- Deploy an API gateway
- Deploy lambdas functions and deployment packages

### Requirements

Verify [aws-cli]() is installed.

Run `aws configure` command to setup your AWS credentials.

Verify [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started#install-terraform) is installed.

```
$ terraform -help
```

Install [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and Configure your AWS credentials using **aws configure**

```
$ aws configure
```

### Deployment

```
git clone https://github.com/asonnellini/Anatomical-stages-radiography-detection.git
```

Move to *iac* folder 

`$ cd .\iac`

Generate a key pair on AWS....


Initialize the directory

```
$ terraform init
```

Check what terraform will do before making the actual changes

```
$ terraform plan
```

Create the infrastructure

```
$ terraform apply
```

ssh connect to the EC2 instance. Wait until the container is in running state
check with `docker ps`.

## Deploy the webapp on heroku


## Run detection


# Authors
