from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_folder='static')

BASE_URL = "https://demo-eu.demo1.pricefx.com"
PARTITION = "demofx_bprasath"
AUTH = ('demofx_bprasath/June-Mahesh', 'start123')
HEADERS = {"Content-Type": "application/json"}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/search_product', methods=['POST'])
def search_product():
    data = request.form
    column = data.get('column')
    value = data.get('value')

    if not column or not value:
        return jsonify({"results": [], "totalResults": 0})

    criteria = []
    if value.lower() != "all":
        criteria = [{
            "fieldName": column,
            "operator": "iContains",
            "value": value
        }]

    payload = {
        "endRow": 10000,  
        "oldValues": None,
        "operationType": "fetch",
        "startRow": 0,
        "textMatchStyle": "substring",
        "data": {
            "_constructor": "AdvancedCriteria",
            "operator": "and",
            "criteria": criteria
        }
    }

    type_code = "P"
    url = f"{BASE_URL}/pricefx/{PARTITION}/fetch/{type_code}"
    response = requests.post(url, json=payload, headers=HEADERS, auth=AUTH)

    if response.status_code != 200:
        return jsonify({"results": [], "totalResults": 0, "error": response.json()})

    response_data = response.json()
    products = response_data.get('response', {}).get('data', [])
    total_results = len(products)

    results = []
    for product in products:
        result = {
            "ProductId": product.get("sku", "null"),
            "ProductFamily": product.get("label", "null"),
            "ProductLine": product.get("attribute21", "null"),
            "ProductGroup": product.get("attribute19", "null"),
            "Status": product.get("attribute10", "null"),
            "ProductSubGroup": product.get("attribute11", "null"),
            "Stock": product.get("attribute12", "null"),
            "Color": product.get("attribute13", "null")
        }
        results.append(result)

    return jsonify({"results": results, "totalResults": total_results})

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    category = data.get('category')
    search_input = data.get('searchInput')
    page = int(data.get('page', 1))
    results_per_page = int(data.get('resultsPerPage', 8))

    if not category or not search_input:
        return jsonify({"results": [], "hasMore": False})

    if search_input.lower() == "all":
        payload = {
            "endRow": 10000, 
            "oldValues": None,
            "operationType": "fetch",
            "startRow": 0,
            "textMatchStyle": "substring",
            "data": {
                "_constructor": "AdvancedCriteria",
                "operator": "and",
                "criteria": [{}]  
            }
        }
    else:
        if category == 'name':
            criteria = [{
                "fieldName": "name", 
                "operator": "iContains",
                "value": search_input
            }]
        else:
            criteria = [{
                "fieldName": category,
                "operator": "iContains",
                "value": search_input
            }]

        payload = {
            "endRow": results_per_page,
            "oldValues": None,
            "operationType": "fetch",
            "startRow": (page - 1) * results_per_page,
            "textMatchStyle": "substring",
            "data": {
                "_constructor": "AdvancedCriteria",
                "operator": "and",
                "criteria": criteria
            }
        }

    url = f"{BASE_URL}/pricefx/{PARTITION}/customermanager.fetchformulafilteredcustomers"
    response = requests.post(url, json=payload, headers=HEADERS, auth=AUTH)
    
    if response.status_code != 200:
        return jsonify({"results": [], "hasMore": False, "error": response.json()})

    response_data = response.json()
    customers = response_data.get('response', {}).get('data', [])
    total_results = response_data.get('response', {}).get('total', 0)

    results = []
    for customer in customers:
        result = {
            "CustomerId": customer.get("customerId", "null"),
            "Customer_Name": customer.get("name", "null"),
            "Country": customer.get("attribute10", "null"),
            "Customer_Currency": customer.get("attribute19", "null")
        }
        results.append(result)

    has_more = (page * results_per_page) < total_results if search_input.lower() != "all" else False

    return jsonify({"results": results, "hasMore": has_more})


if __name__ == '__main__':
    app.run(debug=True)
