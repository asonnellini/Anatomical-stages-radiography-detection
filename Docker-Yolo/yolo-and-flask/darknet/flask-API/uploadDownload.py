"""
This script includes functions used in the flask_api.py script to upload/download files from S3 buckets
to the EC2/Docker container that runs the flask API
"""

import boto3
import botocore
import os

def downloadFromS3(bucket:str, pathInBucket:str, saveAsFileName:str, saveAsPath = ""):
	"""
	This function downloads a file from an S3 bucket to a local folder.
	Input:
		- bucket = S3 bucket name
		- pathInBucket = folder path + file name in the S3 bucket  (e.g. BucketFolder/file.png)
		- saveAsPath =  path on the EC2 where the image will be saved - by default is the empty
		string which means the file will be saved in the same directory where this script 
		is running
		- saveAsFileName = name of the file saved on the EC2
		
	Output:
		- success: True if file was uploaded, else False
		- err = a string with details as to how the upload succeeded or failed
	"""
	
	success = True
	err = "OK"
	
	# if saveAsPath is the empty string, then the  file will be saved in the local folder
	if saveAsPath == "":
		saveAs = saveAsFileName
		
	# else the file will be saved in the folder specified in saveAsPath
	else:
		saveAs = os.path.join(saveAsPath, saveAsFileName)

	print(f"Save path: {saveAs}")

	s3 = boto3.resource('s3')

	print(f"Bucket :{bucket}")
	print(f"pathInBucket : {pathInBucket}")

	try:
		s3.Bucket(bucket).download_file(pathInBucket, saveAs)
		
		print("Downloading")

	except botocore.exceptions.ClientError as e:
		
		success = False
		print("Error occurred")
		if e.response['Error']['Code'] == "404":
	        	err = "The object does not exist."
	        	
		else:
			err = "Cannot download the image from the S3 bucket"

	return success, err


def upload_file(filePath, file_name, bucket, object_name=None):
	"""
	This function uploads a file from the local machine to an S3 bucket.
	Input:
		- filePath = path of the file on the EC2
		- file_name = name of the file on the EC2 to be uploaded to the S3 bucket (e.g. EC2Folder/file.png)
		- bucket = S3 Bucket to upload the file to
		- object_name = S3 object name (e.g. S3/file.png). If not specified then file_name is used
	
	Output:
		- success = True if file was uploaded, else False
		- err = a string with details as to how the upload succeeded or failed
	"""
	
	success = True
	err = "OK"

	# If S3 object_name was not specified, use file_name
	if object_name is None:
		object_name = file_name

	# Upload the file
	s3_client = boto3.client('s3')
	
	fileToUpload = os.path.join(filePath,file_name)
	
	try:
		response = s3_client.upload_file(fileToUpload, bucket, object_name, ExtraArgs={'ACL':'bucket-owner-full-control'})
	
	except ClientError as e:
		logging.error(e)
		success = False
		err = "cannot upload the image in the system"
	
	return success, err
