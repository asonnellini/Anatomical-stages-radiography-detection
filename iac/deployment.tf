provider "aws" {
	region = "us-east-2"
}

resource "aws_iam_role" "yolo_s3_access" {
  name = "yolo_s3_access"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
    "Action": "sts:AssumeRole",
    "Principal": {
        "Service": "ec2.amazonaws.com"
    },
    "Effect": "Allow",
    "Sid": ""
    }
]
}
EOF

  tags = {
      role = "S3FullAccess"
  }
}

resource "aws_iam_instance_profile" "ec2P2_profile" {
  name = "ec2P2_profile"
  role = aws_iam_role.yolo_s3_access.name
}

resource "aws_iam_role_policy" "ec2P2_policy" {
  name = "ec2P2_policy"
  role = aws_iam_role.yolo_s3_access.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_security_group" "basic_security" {
    
    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 8090
        to_port     = 8090
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    }
    
}

resource "aws_s3_bucket" "b" {
  bucket = "deep-yolo-project"
  acl    = "private"
  tags = {
    name  = "yolo-bucket"
    stage = "dev"
  }
}

resource "aws_s3_bucket_object" "setUpToStartYolo" {
    bucket = aws_s3_bucket.b.id
    acl    = "private"
    key    = "setUpToStartYolo/"
}

resource "aws_s3_bucket" "config" {
  bucket = "deep-config"
  acl    = "private"
  tags = {
    name  = "config"
    stage = "dev"
  }
}
variable "upload_directory" {
  default = "../detection/yolo-and-flask/"
}

resource "aws_s3_bucket_object" "yolo-flask" {
  for_each = fileset(var.upload_directory, "*")
  bucket = aws_s3_bucket.config.id
  key    = each.value
  source = "../detection/yolo-and-flask/${each.value}"
  etag   = filemd5("../detection/yolo-and-flask/${each.value}")
}

resource "aws_s3_bucket_object" "darknet" {
    bucket = aws_s3_bucket.config.id
    acl    = "private"
    key    = "darknet/"
}

resource "aws_s3_bucket_object" "cfg" {
    bucket = aws_s3_bucket.config.id
    acl    = "private"
    key    = "darknet/cfg/"
}

resource "aws_s3_bucket_object" "api" {
    bucket = aws_s3_bucket.config.id
    acl    = "private"
    key    = "darknet/flask-API/"
}

resource "aws_s3_bucket_object" "obj" {
    bucket = aws_s3_bucket.config.id
    acl    = "private"
    key    = "darknet/obj-config-files/"
}

resource "aws_s3_bucket_object" "darknet-cfg" {
  for_each = fileset("../detection/yolo-and-flask/darknet/cfg/", "*")
  bucket = aws_s3_bucket.config.id
  key    = "${aws_s3_bucket_object.cfg.key}${each.value}"
  source = "../detection/yolo-and-flask/darknet/cfg/${each.value}"
  etag   = filemd5("../detection/yolo-and-flask/darknet/cfg/${each.value}")
}

resource "aws_s3_bucket_object" "darknet-api" {
  for_each = fileset("../detection/yolo-and-flask/darknet/flask-API/", "*")
  bucket = aws_s3_bucket.config.id
  key    = "${aws_s3_bucket_object.api.key}${each.value}"
  source = "../detection/yolo-and-flask/darknet/flask-API/${each.value}"
  etag   = filemd5("../detection/yolo-and-flask/darknet/flask-API/${each.value}")
}

resource "aws_s3_bucket_object" "darknet-obj" {
  for_each = fileset("../detection/yolo-and-flask/darknet/obj-config-files/", "*")
  bucket = aws_s3_bucket.config.id
  key    = "${aws_s3_bucket_object.obj.key}${each.value}"
  source = "../detection/yolo-and-flask/darknet/obj-config-files/${each.value}"
  etag   = filemd5("../detection/yolo-and-flask/darknet/obj-config-files/${each.value}")
}
#Deep Learning AMI (Ubuntu 18.04) Version 36.0 - ami-01bd6a1621a6968d7
resource "aws_instance" "yolo-instance" {
	ami = "ami-01bd6a1621a6968d7"
	instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.basic_security.id]
  iam_instance_profile = aws_iam_instance_profile.ec2P2_profile.name
	key_name = "ec2-p2" #aws_key_pair.ec2-p2-key.key_name
	user_data = file("user_data.sh")
  tags = {
    name = "yolo-instance"
    type = "t2.micro"
    stage = "dev"
  }
}