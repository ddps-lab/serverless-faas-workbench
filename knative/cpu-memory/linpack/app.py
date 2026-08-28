from numpy import matrix, linalg, random
from time import time
import json
import os
import sys
import re
from flask import Flask, request, jsonify


app = Flask(__name__)

def linpack(n):
    # LINPACK benchmarks
    ops = (2.0 * n) * n * n / 3.0 + (2.0 * n) * n

    # Create AxA array of random numbers -0.5 to 0.5
    A = random.random_sample((n, n)) - 0.5
    B = A.sum(axis=1)

    # Convert to matrices
    A = matrix(A)
    B = matrix(B.reshape((n, 1)))

    # Ax = B
    start = time()
    x = linalg.solve(A, B)
    latency = time() - start

    mflops = (ops * 1e-6 / latency)

    return latency, mflops

@app.route('/', methods=['POST'])
def linpack_main():
    json_from_request = request.json   # parse JSON body

    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    n_operations = json_from_request.get("n")
    metadata = json_from_request.get("metadata", None)
    latency, mflops = linpack(n_operations)
    latencies["function_execution"] = latency
    timestamps["finishing_time"] = time()

    print("Function completed!")    
    return jsonify({'statusCode': 200, "latencies": latencies, "timestamps": timestamps, "metadata": metadata})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))