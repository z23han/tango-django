import json
import urllib, urllib2

BING_API_KEY = 'ApuwFvz3HUc9geDI5E5koYH4A1ntm6XKl/YkWAgPwds'

def run_query(search_terms):
	# Specify the base
	root_url = 'https://api.datamarket.azure.com/Bing/Search/'
	source = 'Web'

	results_per_page = 10
	offset = 0

	# wrap quotes around the query terms as required API, the query would be stored 
	query = "'{0}'".format(search_terms)
	query = urllib.quote(query)

	# construct the latter part of the request's url
	search_url = "{0}{1}?format=json$top={2}&$skip={3}&Query={4}".format(
		root_url, 
		source, 
		results_per_page, 
		offset, 
		query
	)

	# set up authentication with Bing servers, it must be a string and put in API key
	username = ''

	# create password manager which handles authentication for us
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, search_url, username, BING_API_KEY)

	# create results list we'll populate
	results = []

	try:
		# prepare for connecting to Bing's server
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)

		# connect to the server and read response generated
		response = urllib2.urlopen(search_url).read()

		# convert the string response to a python dictionary object
		json_response = json.loads(response)

		# loop through each page returned, populate out the results list
		for result in json_response['d']['results']:
			results.append({
				'title': result['Title'], 
				'link': result['Url'], 
				'summary': result['Description']
			})
	except urllib2.URLError, e:
		print "Error when querying Bing API: ", e
	
	# return the list of results to the calling function. 
	return results