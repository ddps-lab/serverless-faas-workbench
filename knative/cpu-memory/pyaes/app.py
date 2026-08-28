from time import time
import random
import string
import pyaes
from time import time
import json
import os
import sys
import re
from flask import Flask, request, jsonify


app = Flask(__name__)

def generate(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

@app.route('/', methods=['POST'])
def generate_main():
    json_from_request = request.json   # parse JSON body

    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    length_of_message = json_from_request.get("length_of_message")
    num_of_iterations = json_from_request.get("num_of_iterations")
    metadata = json_from_request.get("metadata")

    message = generate(length_of_message)

    # 128-bit key (16 bytes)
    KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'

    start = time()
    for loops in range(num_of_iterations):
        aes = pyaes.AESModeOfOperationCTR(KEY)
        ciphertext = aes.encrypt(message)

        aes = pyaes.AESModeOfOperationCTR(KEY)
        plaintext = aes.decrypt(ciphertext)
        aes = None

    latency = time() - start
    latencies["function_execution"] = latency
    timestamps["finishing_time"] = time()

    print("Function completed!")    
    return jsonify({'statusCode': 200, "latencies": latencies, "timestamps": timestamps, "metadata": metadata})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))