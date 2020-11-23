import json
import requests

def lambda_handler(event, context):

    # defining the api-endpoint  
    API_ENDPOINT = os.environ['API_ENDPOINT']
      
    # data to be sent to api 
    data = {
        'bucketName':event['bucketName'], 
        'folderBucket':event['folderBucket'], 
        'imgFileName':event['imgFileName'], 
        'bucketDestination':event['bucketDestination'],
        'bucketDestFolder': event['bucketDestFolder']
    } 
      
    # sending post request and saving response as response object 
    r = requests.post(url = API_ENDPOINT, data = data) 
      
    # extracting response text  
    # pastebin_url = r.text 
    # print("The pastebin URL is:%s"%pastebin_url) 
    
    return {
        'statusCode': r.status_code,
        'Outcome': r.Outcome, 
        'destBucket': r.destBucket, 
        'destBucketFolder': destinationBucketFolder, 
        'destFileName': EC2FinalImg
        
    }

