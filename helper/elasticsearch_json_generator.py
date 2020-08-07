import json
import sys
from datetime import datetime

def log(msg):
    date_timestamp = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print(date_timestamp + " INFO: " + str(msg.encode(sys.stdout.encoding, 'ignore').decode()))


#in_file_list_name = sys.argv[1]
in_file_list_name = "filelist.txt"
in_file_list = []
out_filename = 'out_final_5120.json'

'''
Create an ElasticSearch instance using the AWS ElasticSearch Service.
- Create an ElasticSearch index called “restaurants”
- Create an ElasticSearch type under the index “restaurants” called “Restaurant”
- Store partial information for each restaurant scraped in ElasticSearch under the “restaurants” index, where each entry has a “Restaurant” data type. This data type
	will be of composite type stored as JSON in ElasticSearch.
https://www.elastic.co/guide/en/elasticsearch/guide/current/mapping.html
- You only need to store RestaurantID and Cuisine for each restaurant

Format -
{ "index" : { "_index": "restaurants", "_type" : "Restaurant", "_id" : "1" } }
{"restaurant_id": "BQRfaq0U75B5EEblBZ2Aqg", "cuisines": ["American (New)", "Bars", "American (Traditional)"]}

curl -XPOST https://search-dining-concierge-chatbot-xwlf5gjwkmqmggvmawl36nit4i.us-east-1.es.amazonaws.com/_bulk --data-binary @out_final.json -H 'Content-Type: application/json'
curl -XPUT https://search-dining-concierge-chatbot-xwlf5gjwkmqmggvmawl36nit4i.us-east-1.es.amazonaws.com/restaurants/Restaurant/1 -d '{"restaurant_id": "testxyz", "cuisines": ["American (New)"]}' -H 'Content-Type: application/json'
curl -XGET 'https://search-dining-concierge-chatbot-xwlf5gjwkmqmggvmawl36nit4i.us-east-1.es.amazonaws.com/restaurants/_search?q=American'
curl -XDELETE 'https://search-dining-concierge-chatbot-xwlf5gjwkmqmggvmawl36nit4i.us-east-1.es.amazonaws.com/restaurants'

'''

index_dict = {}
restaurant_details = {}
index = 1
business_id_cuisines_list_dict = {}

with open(in_file_list_name, 'r') as f:
	in_file_list = f.read().splitlines();

for filename in in_file_list:
	log("Processing " + filename)
	with open(filename, 'r') as f:
		businesses = json.load(f)
	for i in range(len(businesses)):
		business = businesses[i]
		business_id = business["id"]
		business_categories = business["categories"]
		cuisines_list = []
		for j in range(len(business_categories)):
			log(business_id + ' -> ' + business_categories[j]["title"])
			cuisines_list.append(business_categories[j]["title"])
		if not business_id_cuisines_list_dict[business_id] == cuisines_list:
			index_dict["index"] = { "_index": "restaurants", "_type": "Restaurant", "_id": index }
			restaurant_details["restaurant_id"] = business_id
			restaurant_details["cuisines"] = cuisines_list
			index += 1
			business_id_cuisines_list_dict[business_id] = cuisines_list
			with open(out_filename, 'a+') as f:
				json.dump(index_dict, f)
				json.dump(restaurant_details, f)
