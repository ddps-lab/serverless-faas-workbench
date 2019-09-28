import azure.functions as func
from time import time
import string
import random
import pyaes


def generate(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def main(req: func.HttpRequest) -> func.HttpResponse:
    length_of_message = req.params.get('lenght_of_message')
    num_of_iterations = req.params.get('num_of_iterations')\

    message = generate(length_of_message)

    # 128-bit key (16 bytes)
    KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'

    start = time()
    for loops in range(num_of_iterations):
        aes = pyaes.AESModeOfOperationCTR(KEY)
        ciphertext = aes.encrypt(message)
        print(ciphertext)

        aes = pyaes.AESModeOfOperationCTR(KEY)
        plaintext = aes.decrypt(ciphertext)
        print(plaintext)
        aes = None

    latency = time() - start

    return func.HttpResponse(str(latency))
