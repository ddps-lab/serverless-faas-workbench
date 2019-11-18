from google.cloud import storage
import gcsfs
from time import time 
import json


storage_client = storage.Client()
subs = "</title><text>"
computer_language = ["JavaScript", "Java", "PHP", "Python", "C#", "C++", 
    "Ruby", "CSS", "Objective-C", "Perl",        
    "Scala", "Haskell", "MATLAB", "Clojure", "Groovy"]


def function_handler(request):
    request_json = request.get_json(silent=True)
    job_bucket = request_json['job_bucket']
    dataset_bucket = request_json['dataset_bucket']
    dataset_keys = request_json['dataset_keys']
    mapper_id = request_json['mapper_id']
    
    d_bucket = storage_client.get_bucket(dataset_bucket)
    j_bucket = storage_client.get_bucket(job_bucket)
    
    output = {}
    for lang in computer_language:
        output[lang] = 0
    
    network = 0
    map = 0
    keys = dataset_keys.split('/')
    
    # Download and process all keys
    for key in keys:
        blob = d_bucket.blob(key)
        job_blob = j_bucket.blob(str(mapper_id))
        
        start = time()
        data = blob.download_as_string().decode("utf-8")
        network += time() - start
        
        start = time()
        for line in str(data).split('\n')[:-1]:
            try:
                idx = line.find(subs)
                text = line[idx + len(subs): len(line)-16]
                for lang in computer_language:
                    if lang in text:
                        output[lang] += 1
                        
            except Exception:
                print("Error")
        map += time() - start
        
        start = time()
        job_blob.upload_from_string(json.dumps(output))
        network += time() - start

        print(output)
    
    result = {
        'network': str(network),
        'map': str(map)
    }
    
    return json.dumps(result)
