import json
import requests
#import pickle
import os

def lambda_handler(event, context):

    # defining the api-endpoint  
    url = os.environ['API_ENDPOINT']
      
    # data to be sent to api 
    payload = {
        "bucketName": event['bucketName'], 
        "folderBucket": event['folderBucket'], 
        "imgFileName": event['imgFileName'], 
        "bucketDestination": event['bucketDestination'],
        "bucketDestFolder": event['bucketDestFolder']
    }
    
    headers = { 'Content-Type': 'application/json' }
      
    # sending post request and saving response as response object

    response = requests.request("POST", url, headers=headers, data=payload)

    

    return {
    'statusCode': 201
    #'response' : pickle.dumps(response)
    }