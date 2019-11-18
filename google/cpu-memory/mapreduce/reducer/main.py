from google.cloud import storage
import gcsfs
from time import time
import json

storage_client = storage.Client()
computer_language = ["JavaScript", "Java", "PHP", "Python", "C#", "C++",
                     "Ruby", "CSS", "Objective-C", "Perl",
                     "Scala", "Haskell", "MATLAB", "Clojure", "Groovy"]


def function_handler(request):
    request_json = request.get_json(silent=True)
    job_bucket = request_json['job_bucket']

    j_bucket = storage_client.get_bucket(job_bucket)
    job_blobs = j_bucket.list_blobs()
    all_keys = []
    for j_blob in job_blobs:
        all_keys.append(j_blob.name)

    output = {}

    for lang in computer_language:
        output[lang] = 0

    network = 0
    reduce = 0

    for key in all_keys:
        job_blob = j_bucket.blob(key)

        start = time()
        data = job_blob.download_as_string().decode("utf-8")
        network += time() - start

        start = time()
        json_data = json.loads(data)
        for key in json_data:
            output[key] += int(json_data[key])
        reduce += time() - start

    result = {
        'network': str(network),
        'reduce': str(reduce)
    }

    return json.dumps(result)
