from flask import Flask, render_template, request
import boto3
import requests
import json
import typing

app = Flask(__name__)
from werkzeug.utils import secure_filename
#import key_config as keys

#htmlPage = "index2.html"
htmlPage = "home.html"

def invokeLambdaFunction(*, functionName:str=None, payload:typing.Mapping[str, str]=None):
    if  functionName == None:
        raise Exception('ERROR: functionName parameter cannot be NULL')
    payloadStr = json.dumps(payload)
    payloadBytesArr = bytes(payloadStr, encoding='utf8')
    client = boto3.client('lambda',region_name='eu-west-3')
    response = client.invoke(
        FunctionName=functionName,
        InvocationType="RequestResponse",
        Payload=payloadBytesArr
    )
    return response




s3 = boto3.client('s3')

BUCKET_NAME = 'yolo-project'


@app.route('/')
def home():
    return render_template(htmlPage)


@app.route('/upload', methods=['post'])
def upload():
    if request.method == 'POST':
        img = request.files['file']
        print(img)
        if img:
            filename = secure_filename(img.filename)
            img.save(filename)
            s3.upload_file(
                Bucket=BUCKET_NAME,
                Filename=filename,
                Key="toDetect" + "/" + filename
            )
            msg = "Upload Done ! "

        headers = {'Content-Type': 'application/json'}

        data = {"bucketName": "yolo-project", "folderBucket": "toDetect", "imgFileName": filename, "bucketDestination": "yolo-detection", "bucketDestFolder": "detected"}

        # response = requests.post('http://3.135.40.94:8090/', headers=headers, data=data)
	# The below lambda function triggers the detection on the backend and returns the signed URL that can be used to download the detected image from the bucket 
        r = invokeLambdaFunction(functionName ='triggerDetection',  payload = data)
        t = r['Payload']
        j = json.loads(t.read().decode("utf-8"))
	
	

        #finalURL = t["presigned_url"]    #j.decode("utf-8")["presigned_url"]   #json.dumps(j.decode("utf-8"))["presigned_url"]

    return render_template(htmlPage, msg = j["presigned_url"] )


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000,debug=True)
