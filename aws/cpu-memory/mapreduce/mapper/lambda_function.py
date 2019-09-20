import json
import boto3
from time import time

# Create S3 session
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

subs = "</title><text>"
computer_language = ["JavaScript", "Java", "PHP", "Python", "C#", "C++",
                     "Ruby", "CSS", "Objective-C", "Perl",
                     "Scala", "Haskell", "MATLAB", "Clojure", "Groovy"]


def write_to_s3(bucket, key, data, metadata):
    s3.Bucket(bucket).put_object(Key=key, Body=data, Metadata=metadata)


def lambda_handler(event, context):
    job_bucket = event['job_bucket']
    src_bucket = event['bucket']
    src_keys = event['keys']
    mapper_id = event['mapper_id']

    output = {}

    for lang in computer_language:
        output[lang] = 0

    network = 0
    map = 0
    keys = src_keys.split('/')

    # Download and process all keys
    for key in keys:
        print(key)
        start = time()
        response = s3_client.get_object(Bucket=src_bucket, Key=key)
        contents = response['Body'].read()
        network += time() - start

        start = time()
        for line in contents.split('\n')[:-1]:
            idx = line.find(subs)
            text = line[idx + len(subs): len(line) - 16]
            for lang in computer_language:
                if lang in text:
                    output[lang] += 1

        map += time() - start

    print(output)

    metadata = {
        'output': '%s' % (output),
        'network': '%s' % (network),
        'map': '%s' % (map)
    }

    key = '%s' % (mapper_id)
    write_to_s3(job_bucket, key, json.dumps(output), metadata)

    return json.dumps(metadata)