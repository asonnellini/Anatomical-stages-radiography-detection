from flask import Flask, request
from flask_restful import Resource, Api

import uploadDownload as ud
import os
from shutil import copyfile

import detect2

app = Flask(__name__)
api = Api(app)


class RunDetection(Resource):
	def get(self):
		return {'about': 'This is the Flask API running on the Docker container that hosts Yolo'}

	def post(self):
	
		######### Download the image from the S3 bucket #########
		
		# store the json posted by the caller
		input_json = request.get_json()
		
		#parse the json
		bucket = input_json["bucketName"]
		folderBucket =  input_json["folderBucket"]
		fileName = input_json["imgFileName"]
		destinationBucket = input_json["bucketDestination"]
		destinationBucketFolder = input_json["bucketDestFolder"]
		
		# if the file on S3 is not stored on any S3 folder, then pathInBucket is just the file name
		if folderBucket == "":
			pathInBucket = fileName
		
		# else if the file is stored in an S3 folder, pathInBucket is the concatenation of the folder name and the file name
		else:
			pathInBucket = folderBucket + "/" + fileName
		
		# Path where to store the Image downloaded from the S3 bucket
		EC2path = "/code/images/toDetect"
		
		# Save the file with the following name
		EC2FileName = fileName
		
		# Download the file from the S3 bucket and store it in EC2path
		## TO IMPROVE: the filename on the EC2 should be enhanced to ensure there are no conflicts among various files being uploaded
		dwlSuccess, dwlErr = ud.downloadFromS3(bucket, pathInBucket, EC2FileName, EC2path)
		
		if dwlSuccess != True:
			print("Error in download")
			return {'Outcome': dwlErr }, 201
		
		print("Download OK")

		######### Run the detection #########

		# Path where the image outputted by the detection will be stored on the EC2
		EC2pathFinalImg = "/code/images/detected"

                # Name of the image file outputted by the detection
		EC2FinalImg = "detected_" + fileName

		# perform the detection and save the ouput image into EC2pathFinalImg + "/" + EC2FinalImg
		detect2.detectImg(EC2path + "/" + EC2FileName, EC2pathFinalImg + "/" + EC2FinalImg)

		#upon detection, remove the input image
		if os.path.exists(os.path.join(EC2path, EC2FileName)):
			os.remove(os.path.join(EC2path, EC2FileName))
		else:
			print("The file does not exist")
			
		######### Upload the output image on the S3 ######### 
		
		# Destination file object on S3
		if destinationBucketFolder == "":
			destinationFile = EC2FinalImg
		
		# else if the file is stored in an S3 folder, pathInBucket is the concatenation of the folder name and the file name
		else:
			destinationFile = destinationBucketFolder + "/" + EC2FinalImg
		
		# Upload detected file to bucket yolo-detected
		uplSuccess, uplErr = ud.upload_file(EC2pathFinalImg, EC2FinalImg, destinationBucket, destinationFile)
		
		if uplSuccess != True:
			print("Error in upload")
			return {'Outcome': uplErr }, 201
		
		print("Upload Succesful")
		
		# upon upload, delete the detected image
		if os.path.exists(os.path.join(EC2pathFinalImg, EC2FinalImg)):
			os.remove(os.path.join(EC2pathFinalImg, EC2FinalImg))
		else:
			print("The file does not exist")

		return {'status_code': '201', 'destBucket': destinationBucket, 'destBucketFolder': destinationBucketFolder, 'destFileName': EC2FinalImg} #, 201

api.add_resource(RunDetection, '/')


if __name__ == '__main__' :
	app.run(host = '0.0.0.0', port = 8090, debug = True)



