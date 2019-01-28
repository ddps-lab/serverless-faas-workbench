"""
Various utility functions
"""
import math
import random
import string
import logging

from py3iperf3.iperf3_api import COOKIE_SIZE

DEC_BIT = ['bits', 'Kibs', 'Mibs', 'Gibs', 'Tibs', 'Pibs']
DEC_BYTE = ['Byte', 'KiBytes', 'MiBytes', 'GiBytes', 'TiBytes', 'PiBytes']
BIN_BIT = ['bits', 'Kbits', 'Mbits', 'Gbits', 'Tbits', 'Pbits']
BIN_BYTE = ['Bytes', 'KBytes', 'MBytes', 'GBytes', 'TBytes', 'PBytes']

def make_cookie():
    """Make a test cookie"""

    alphabet = string.ascii_letters + string.digits
    cookie = ''

    for _ in range(COOKIE_SIZE):
        cookie += random.choice(alphabet)

    cookie += '\0'

    return cookie

def setup_logging(debug=False, log_filename=None, **kwargs):
    """Setup logging infrastructure"""

    logger = logging.getLogger('py3iperf3')
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    log_formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)

    logger.addHandler(stream_handler)

    if log_filename is not None:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

def exact_formatter(size_in_bits, dimmesion):
    """Format value to specific prefix"""

    bin_bit_dimm = {
        'k':1,
        'm':2,
        'g':3,
        't':4,
        'p':5
    }

    size_index = bin_bit_dimm.get(dimmesion.lower(), 1)

    if dimmesion[0].isupper():
        # Bytes
        digit_string = '{:.2f}'.format((size_in_bits / 8) / 10**(3 * size_index))
        postfix = DEC_BYTE[size_index]
    else:
        # bits
        digit_string = '{:.2f}'.format(size_in_bits / 10**(3 * size_index))
        postfix = DEC_BIT[size_index]

    digit_string = digit_string.rstrip('0').rstrip('.') if '.' in digit_string else digit_string
    return '{} {}'.format(digit_string, postfix)

def data_size_formatter(size_in_bits, decimal=False, in_bytes=False, dimmension=None):
    """Format size in bits to required dimmension"""

    if size_in_bits < 0:
        # Error?
        return data_size_formatter(-size_in_bits, decimal, in_bytes)

    if size_in_bits == 0:
        return '0 bit'

    # If exact dimmension is given - use it
    if dimmension:
        return exact_formatter(size_in_bits, dimmension)

    if decimal:
        # Decimal format
        postfix = DEC_BIT
        size_val = size_in_bits

        if in_bytes:
            size_val = size_in_bits / 8
            postfix = DEC_BYTE

        size_index = min([len(postfix)-1, int(math.floor(math.log10(size_val)/3))])
        digit_string = '{:.2f}'.format(size_val / 10**(3 * size_index))

    else:
        # Binary format
        postfix = BIN_BIT
        size_val = size_in_bits

        if in_bytes:
            size_val = size_in_bits / 8
            postfix = BIN_BYTE

        size_index = min([len(postfix)-1, int(math.floor(math.log2(size_val)/10))])
        digit_string = '{:.2f}'.format(size_val / 1024**size_index)

    digit_string = digit_string.rstrip('0').rstrip('.') if '.' in digit_string else digit_string
    return '{} {}'.format(digit_string, postfix[size_index])
