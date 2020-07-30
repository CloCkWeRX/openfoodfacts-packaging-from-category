#!/usr/bin/env python

import requests, logging, urllib, argparse, json, sys, operator, collections
from jsonpath_rw import jsonpath, parse

parser = argparse.ArgumentParser()
parser.add_argument("--country", default="world", help="The country you want to examine. Defaults to world.")
parser.add_argument("--debug")

parser.add_argument("category", help="Category you want to examine. Try cake-mixes.")

args = parser.parse_args()

if args.debug == "1":
	logging.basicConfig(stream=sys.stdout, level=logging.INFO)
if args.debug == "2":
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def summarize_packaging(data):
	query = parse('$.products[*].packaging_tags')

	packaging_summary = {}


	for match in query.find(data):
		logging.debug(match.value)
		for packaging in match.value:
			packaging_summary[packaging] = packaging_summary.get(packaging, 0) + 1

	return packaging_summary

def more_to_fetch(data, page):
	count = parse('$.count').find(data)[0].value
	page_size = parse('$.page_size').find(data)[0].value
	index = (page_size * page)

	logging.info("Total: {count}, Current page: {index}".format(count=count, index=index))
	return count > index

def fetch_products(category, country, page = 1):
	url = "https://{country}.openfoodfacts.org/state/packaging-code-completed/category/{category}/{page}.json".format(country=urllib.quote(country), category=urllib.quote(category), page=page)
	logging.info("Fetching " + url)
	response = requests.get(url)

	if response.status_code == 200:
		logging.debug("Success: " + response.text)

		return json.loads(response.text)
	else:
		logging.error("Failed with {code}\n{body}".format(code=response.status_code, body=response.text))

		return None


page = 1
data = fetch_products(args.category, args.country, page)

if data != None:
	packaging_summary = summarize_packaging(data)
	while more_to_fetch(data, page):
		logging.debug(packaging_summary)

		page += 1
		data = fetch_products(args.category, args.country, page)

		if data == None:
			break

		additional_summary = summarize_packaging(data)
		packaging_summary.update(additional_summary)
		if page > 2:
			logging.info("Fetched maximum pages, halting")
			break

	overall_summary = collections.OrderedDict()
	for packaging, count in sorted(packaging_summary.items(), key=operator.itemgetter(1), reverse=True):
		overall_summary[packaging] = count

	print json.dumps(overall_summary)

