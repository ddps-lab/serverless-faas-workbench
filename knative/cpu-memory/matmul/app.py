import numpy as np
from time import time
import json
import os
import sys
import re
from flask import Flask, request, jsonify


app = Flask(__name__)

def matmul(n):
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)

    start = time()
    C = np.matmul(A, B)
    latency = time() - start
    return latency

@app.route('/', methods=['POST'])
def matmul_main():
    json_from_request = request.json   # parse JSON body

    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    n_operations = json_from_request.get("n")
    metadata = json_from_request.get("metadata", None)
    result = matmul(n_operations)
    latencies["function_execution"] = result
    timestamps["finishing_time"] = time()

    print("Function completed!")    
    return jsonify({'statusCode': 200, "latencies": latencies, "timestamps": timestamps, "metadata": metadata})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))