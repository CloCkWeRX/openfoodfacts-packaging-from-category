#!/usr/bin/env python

import requests, logging, urllib, argparse, json, sys, operator
from jsonpath_rw import jsonpath, parse

parser = argparse.ArgumentParser()
parser.add_argument("--country", default="world", help="The country you want to examine. Defaults to world.")
parser.add_argument("--debug")

parser.add_argument("category", help="Category you want to examine. Try cake-mixes.")

args = parser.parse_args()

if args.debug:
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


url = "https://{country}.openfoodfacts.org/state/packaging-code-completed/category/{category}.json".format(country=urllib.quote(args.country), category=urllib.quote(args.category))
logging.debug("Fetching " + url)
response = requests.get(url)
if response.status_code == 200:
	logging.debug("Success: " + response.text)
	data = json.loads(response.text)

	query = parse('$.products[*].packaging_tags')

	packaging_summary = {}


	for match in query.find(data):
		logging.debug(match.value)
		for packaging in match.value:
			packaging_summary[packaging] = packaging_summary.get(packaging, 0) + 1

	sorted_summary = sorted(packaging_summary.items(), key=operator.itemgetter(1), reverse=True)
	print json.dumps(sorted_summary)

else:
	logging.error("Failed with {code}\n{body}".format(code=response.status_code, body=response.text))