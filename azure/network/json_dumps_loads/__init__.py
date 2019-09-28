import azure.functions as func
from urllib.request import urlopen
from time import time
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    link = req.params.get('link') # https://github.com/jdorfman/awesome-json-datasets

    start = time()
    f = urlopen(link)
    data = f.read().decode("utf-8")
    network = time() - start

    start = time()
    json_data = json.loads(data)
    str_json = json.dumps(json_data, indent=4)
    latency = time() - start

    return func.HttpResponse("latency : " + str(latency) + "/ network : " + str(network))
