import json
import boto3
from time import time

# Create S3 session
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

computer_language = ["JavaScript", "Java", "PHP", "Python", "C#", "C++",
                     "Ruby", "CSS", "Objective-C", "Perl",
                     "Scala", "Haskell", "MATLAB", "Clojure", "Groovy"]


def lambda_handler(event, context):
    job_bucket = event['job_bucket']

    output = {}

    for lang in computer_language:
        output[lang] = 0

    network = 0
    reduce = 0

    all_keys = []
    for obj in s3.Bucket(job_bucket).objects.all():
        all_keys.append(obj.key)

    for key in all_keys:
        start = time()
        response = s3_client.get_object(Bucket=job_bucket, Key=key)
        contents = response['Body'].read()
        network += time() - start

        start = time()
        data = json.loads(contents)
        for key in data:
            output[key] += data[key]
        reduce += time() - start

    metadata = {
        'output': str(output),
        'network': str(network),
        'reduce': str(reduce)
    }

    return json.dumps(metadata)
