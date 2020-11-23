import json
import base64
import boto3
import uuid
import logging
import imghdr
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    s3 = boto3.client("s3")
    
    get_file_content= event["content"]
    
    decoded_content = base64.b64decode(get_file_content)

    response = {}
    # get extension from content
    for tf in imghdr.tests:
        extention = tf(decoded_content, None)
        if extention:
            break;
    print("Extensionof the Image: ",extention)
    if(extention==None): # if res is None then BASE64 is of not an image.
    
        response["statusCode"] = 400
        response["message"] = "It is not image, Only images allowed"
    
    else:
        # It is an image
        # generate a unique identifier for the image
        region ="eu-west-3"
        bucket = "my-yolo-project"
        folder = "toDetect"
        name = str(uuid.uuid4()) + extension
        key = folder + "/" + name
        url = f"https://{bucket}.s3-{region}.amazonaws.com/{key}"

        try:
            s3_upload = s3.put_object(Bucket=bucket, Key=key, Body=decoded_content)
            
            #presigned_url = create_presigned_url(bucket, key)
            response["statusCode"] = 201
            response["bucketName"] = bucket
            response["folderBucket"] = "toDetect"
            response["imgFileName"] = name
            response["bucketDestination"] = bucket
            response["bucketDestFolder"] = "detected"
        
        except Exception as e:
            raise (e)
        
    return response

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_url("get_object",
                                                    Params={"Bucket": bucket_name,
                                                            "Key": object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
    