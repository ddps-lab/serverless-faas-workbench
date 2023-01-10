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


def main(event):
    latencies = {}
    timestamps = {}
    timestamps["starting_time"] = time()
    n = int(event['n'])
    metadata = event['metadata']
    latency = float_operations(n)
    latencies["function_execution"] = latency
    timestamps["finishing_time"] = time()
    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}