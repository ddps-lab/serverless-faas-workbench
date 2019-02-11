import boto3
from time import time

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    bucket = event['input_bucket']
    s3_bucket = s3.Bucket(bucket)

    result = set()
    latency = 0

    for obj in s3_bucket.objects.all():
        body = obj.get()['Body'].read()
        start = time()
        feature = body.replace("'", '').split(',')
        result.update(feature)
        latency += time() - start

    print(len(result))
    print(latency)
    
    write_key = "result.txt"
    s3_client.put_object(Body=str(result), Bucket=bucket, Key=write_key)

    return latency
