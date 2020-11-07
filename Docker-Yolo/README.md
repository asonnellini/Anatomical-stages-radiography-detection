# Deploy Yolo on AWS EC2 Instance

We use Infrastructure as Code approach to deploy yolo on AWS EC2/P2 instance.

In the following we automatically:

- Provision the instance
- Install docker on the instance
- Deploy a containter with yolo
- In that container deploy a REST API to perform anatomical stage radiography detection on request.

## Requirements

Verify [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started#install-terraform) is installed.

```
$ terraform -help
```

Install [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and Configure your AWS credentials using **aws configure**

```
$ aws configure
```

## Deployment

`git clone <GIT_HUB_REPOSITORY>`

Move to *iac* folder 

`$ cd .\iac`

Generate public/private rsa key pair.
```
$ ssh-keygen -t rsa
```

In this deployment we saved the public key **key.pub** in the current working directory.

Setup correct permission to the keys:
```
$ chmod 400 key*
```

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

Inspect state

```
$ terraform show
```

## Perform detection
