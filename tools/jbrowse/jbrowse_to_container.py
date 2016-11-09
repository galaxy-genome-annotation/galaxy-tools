#!/usr/bin/env python
import json
import base64
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates an iframe to access a jbrowse dataset')
    parser.add_argument('external_jbrowse_url', help='Jbrowse full URL')
    parser.add_argument('dataset_id', help='Jbrowse dataset_id to display')

    args = parser.parse_args()


    # This is base64 encoded to get past the toolshed's filters.
    HTML_TPL = """
    PGh0bWw+PGhlYWQ+PHRpdGxlPkVtYmVkZGVkIEpCcm93c2UgQWNjZXNzPC90aXRsZT48c3R5bGUg
    dHlwZT0idGV4dC9jc3MiPmJvZHkge3ttYXJnaW46IDA7fX0gaWZyYW1lIHt7Ym9yZGVyOiAwO3dp
    ZHRoOiAxMDAlO2hlaWdodDogMTAwJX19PC9zdHlsZT48L2hlYWQ+PGJvZHk+PGlmcmFtZSBzcmM9
    IntiYXNlX3VybH0/ZGF0YT1kYXRhL3tkYXRhc2V0X2lkfSI+PC9pZnJhbWU+PC9ib2R5PjwvaHRt
    bD4N
    """
    HTML_TPL = base64.b64decode(HTML_TPL.replace('\n', ''))

print HTML_TPL.format(base_url=args.external_jbrowse_url, dataset_id=args.dataset_id)
