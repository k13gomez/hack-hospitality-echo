import requests
def getOrderTotal():
	r = requests.get('http://redash-dev.hack-hospitality-fitlife.k13labs.com/api/queries/6/results.json?api_key=AIER9n6VOq0NWGZMZwwO3XZz9QEpTs7ueyYKcymK')
	rows = dict(r.json())['query_result']['data']['rows'][0]['order_total']
	print (rows)
	return rows

getOrderTotal()
	