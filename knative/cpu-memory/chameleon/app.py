from time import time
import six
import json
import os
import sys
import re
from flask import Flask, request, jsonify
from chameleon import PageTemplate
import argparse


BIGTABLE_ZPT = """\
<table xmlns="http://www.w3.org/1999/xhtml"
xmlns:tal="http://xml.zope.org/namespaces/tal">
<tr tal:repeat="row python: options['table']">
<td tal:repeat="c python: row.values()">
<span tal:define="d python: c + 1"
tal:attributes="class python: 'column-' + %s(d)"
tal:content="python: d" />
</td>
</tr>
</table>""" % six.text_type.__name__

app = Flask(__name__)

def update_args_from_json(args, json_data):
    for key, value in json_data.items():
        if key == 'cpu-work':
            value = int(value)
        
        if key == 'percent-cpu':
            value = float(value)

        setattr(args, key.replace("-", "_"), value)
        
    return args

@app.route('/', methods=['POST'])
def chameleon():

    json_from_request = request.json   # parse JSON body
    num_of_rows = json_from_request.get("num_of_rows")
    num_of_cols = json_from_request.get("num_of_cols")
    metadata = json_from_request.get("metadata", None)

    latencies = {}
    timestamps = {}
    timestamps["starting_time"] = time()

    start = time()
    tmpl = PageTemplate(BIGTABLE_ZPT)

    data = {}
    for i in range(num_of_cols):
        data[str(i)] = i

    table = [data for x in range(num_of_rows)]
    options = {'table': table}

    data = tmpl.render(options=options)
    latency = time() - start
    latencies["function_execution"] = latency
    timestamps["finishing_time"] = time()
    
    print("Function completed!")    
    return jsonify({'statusCode': 200, "latencies": latencies, "timestamps": timestamps, "metadata": metadata})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))    