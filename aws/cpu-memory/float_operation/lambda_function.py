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

def lambda_handler(event, context):
    N = int(event['N'])
    result = float_operations(N)
    print(result)
    return result
