from time import time
import random
import string
import pyaes


def generate(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def main(event):
    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    length_of_message = event['length_of_message']
    num_of_iterations = event['num_of_iterations']
    metadata = event['metadata']

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

    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}