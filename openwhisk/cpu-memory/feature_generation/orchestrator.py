import boto3
import json
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool

import requests

s3 = boto3.resource('s3')
lambda_client = boto3.client('lambda')

wsk_host = "http://172.17.0.1:3233"


def invoke(action, payload):
    url = f"http://{wsk_host}/api/v1/namespaces/guest/actions/{action}?blocking=true"

    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A='
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    return response.json()['response']


def invoke_lambda(output_bucket, key):
    invoke(
        action='feature_extractor',
        payload=json.dumps({
            "key": key,
            "output_bucket": output_bucket
        })
    )


def main(args):
    bucket = args['input_bucket']

    all_keys = []

    for obj in s3.Bucket(bucket).objects.all():
        all_keys.append(obj.key)

    print("Number of File : " + str(len(all_keys)))
    print("File : " + str(all_keys))

    pool = ThreadPool(len(all_keys))
    pool.map(partial(invoke_lambda, bucket), all_keys)
    pool.close()
    pool.join()

    return {"num_of_file": len(all_keys)}

