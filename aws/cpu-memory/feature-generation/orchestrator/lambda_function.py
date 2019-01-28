import boto3
import json
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

s3 = boto3.resource('s3')
lambda_client = boto3.client('lambda')

def invoke_lambda(key):
    resp = lambda_client.invoke(
        FunctionName = 'feature_generation',
        InvocationType = 'RequestResponse',
        Payload = json.dumps({
            "input_bucket": "kmu-serverless-lambda-dataset",
            "key": key
        }))

def lambda_handler(event, context):
    bucket = event['bucket'] 
    all_keys = []
    for obj in s3.Bucket(bucket).objects.all():
        all_keys.append(obj.key)
    print "Number of File : " + str(len(all_keys))
    print "File : " + str(all_keys)
    
    pool = ThreadPool(len(all_keys))
    pool.map(invoke_lambda, all_keys)
    pool.close()
    pool.join()
    
    return {"num_of_file" : str(len(all_keys))}