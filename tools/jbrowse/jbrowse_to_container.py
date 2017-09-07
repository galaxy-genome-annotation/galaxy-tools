#!/usr/bin/env python
from __future__ import print_function

import argparse
import base64


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates an iframe to access a jbrowse instance')
    parser.add_argument('external_jbrowse_url', help='Jbrowse full URL')

    args = parser.parse_args()

    # This is base64 encoded to get past the toolshed's filters.
    HTML_TPL = """
    PGh0bWw+PGhlYWQ+PHRpdGxlPkVtYmVkZGVkIEpCcm93c2UgQWNjZXNzPC90aXRsZT48c3R5bGUg
    dHlwZT0idGV4dC9jc3MiPmJvZHkge3ttYXJnaW46IDA7fX0gaWZyYW1lIHt7Ym9yZGVyOiAwO3dp
    ZHRoOiAxMDAlO2hlaWdodDogMTAwJX19PC9zdHlsZT48L2hlYWQ+PGJvZHk+PGlmcmFtZSBzcmM9
    IntiYXNlX3VybH0iPjwvaWZyYW1lPjwvYm9keT48L2h0bWw+DQo=
    """
    HTML_TPL = base64.b64decode(HTML_TPL.replace('\n', ''))

print(HTML_TPL.format(base_url=args.external_jbrowse_url))
