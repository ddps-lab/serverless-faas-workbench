import math
from time import time


def float_operations(n):
    start = time()
    for i in range(0, n):
        sin_i = math.sin(i)
        cos_i = math.cos(i)
        sqrt_i = math.sqrt(i)
    latency = time() - start
    return latency


def lambda_handler(event, context):
    n = int(event['n'])
    result = float_operations(n)
    print(result)
    return result
