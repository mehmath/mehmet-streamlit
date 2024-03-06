# from urllib2 import Request, urlopen
# from urllib import urlencode, quote_plus
# url = 'https://api.yapikredi.com.tr/api/stockmarket/v1/bistIndices'
# request = Request(url)
# request.get_method = lambda: 'GET'
# response_body = urlopen(request).read()
# print response_body


import json
import requests

# URL'yi güncelleyin, gerektiği şekilde.
URL = "https://api.yapikredi.com.tr/api/stockmarket/v1/bistIndices"

PAGE_NUMBER = 2
PAGE_SIZE = 5

querystring = {"pageNumber": str(PAGE_NUMBER), "pageSize": str(PAGE_SIZE)}

response = requests.request("GET", URL, timeout=3)

print(response)

# data = json.loads(response.text)
# print(json.dumps(data, indent=2))
