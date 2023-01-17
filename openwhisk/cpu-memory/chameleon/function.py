from time import time
import six
import json
from chameleon import PageTemplate


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


def main(event):
    latencies = {}
    timestamps = {}
    timestamps["starting_time"] = time()
    num_of_rows = event['num_of_rows']
    num_of_cols = event['num_of_cols']
    metadata = event['metadata']

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

    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}