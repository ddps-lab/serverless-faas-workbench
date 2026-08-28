import math
from time import time
import json
import os
import sys
import re
from flask import Flask, request, jsonify


app = Flask(__name__)

def float_operations(n):
    start = time()
    for i in range(0, n):
        sin_i = math.sin(i)
        cos_i = math.cos(i)
        sqrt_i = math.sqrt(i)
    latency = time() - start
    return latency

@app.route('/', methods=['POST'])
def float_operations_main():
    json_from_request = request.json   # parse JSON body

    latencies = {}
    timestamps = {}
    timestamps["starting_time"] = time()

    n_operations = json_from_request.get("n")
    metadata = json_from_request.get("metadata", None)
    latency = float_operations(n_operations)

    latencies["function_execution"] = latency
    timestamps["finishing_time"] = time()

    print("Function completed!")    
    return jsonify({'statusCode': 200, "latencies": latencies, "timestamps": timestamps, "metadata": metadata})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))    