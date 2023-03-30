import boto3

s3 = boto3.resource('s3')


def main(args):
    num_of_file = int(args['num_of_file'])
    bucket = args['input_bucket']
    all_keys = []

    for obj in s3.Bucket(bucket).objects.all():
        all_keys.append(obj.key)
    print("Number of File : " + str(len(all_keys)))
    
    if num_of_file == len(all_keys):
        return {"status": "SUCCEEDED"}
    else:
        return {"status": "FAILED"}

