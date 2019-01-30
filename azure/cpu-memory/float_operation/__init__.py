import azure.functions as func
import logging
import math
from time import time

def float_operations(N):
    start = time()
    for i in range(0, N):
        sin_i = math.sin(i)
        cos_i = math.cos(i)
        sqrt_i = math.sqrt(i)
    latency = time() - start
    return latency


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    N = req.params.get('N')
    N = int(N)
    latency = float_operations(N)
    logging.info(latency)
    return func.HttpResponse(str(latency))