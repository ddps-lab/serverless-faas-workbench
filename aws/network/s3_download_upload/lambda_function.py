import boto3
from time import time

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    object_key = event['object_key']
    src_bucket = event['src_bucket']
    dst_bucket = event['dst_bucket']
    path = '/tmp/'+object_key
    start = time()
    s3_client.download_file(src_bucket, object_key, path)
    download_time = time() - start
    print("Download time : " + str(download_time))

    start = time()
    s3_client.upload_file(path, dst_bucket, object_key)
    upload_time = time() - start
    print("Upload time : " + str(upload_time))

    return "download_time : " + download_time + "(s) upload_time : " + upload_time + "(s)"