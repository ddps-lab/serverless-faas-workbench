import boto3
from time import time
from sklearn.feature_extraction.text import TfidfVectorizer

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')


def main(args):
    bucket = args['input_bucket']
    s3_bucket = s3.Bucket(bucket)

    result = []
    latency = 0

    for obj in s3_bucket.objects.all():
        body = obj.get()['Body'].read()
        start = time()
        word = body.replace("'", '').split(',')
        result.extend(word)
        latency += time() - start

    print(len(result))

    tfidf_vect = TfidfVectorizer().fit(result)
    feature = str(tfidf_vect.get_feature_names())
    feature = feature.lstrip('[').rstrip(']').replace(' ', '')

    feature_key = 'feature.txt'
    s3_client.put_object(Body=str(feature), Bucket=bucket, Key=feature_key)

    return {"latency": latency}



