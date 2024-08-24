from flask import Flask, request, render_template
import requests

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    column = request.form.get("column")
    value = request.form.get("value")
    page = int(request.form.get("page", 1))
    
    type_code = "P"
    base_url = "demo-eu.demo1.pricefx.com"
    partition = "demofx_bprasath"
    url = f"https://{base_url}/pricefx/{partition}/fetch/{type_code}"

    items_per_page = 5
    start_row = (page - 1) * items_per_page
    end_row = start_row + items_per_page

    payload = {
        "endRow": end_row,
        "oldValues": None,
        "operationType": "fetch",
        "startRow": start_row,
        "textMatchStyle": "exact",
        "data": {
            "_constructor": "AdvancedCriteria",
            "operator": "and",
            "criteria": [
                {
                    "fieldName": column,
                    "operator": "contains",
                    "value": value if value.lower() != 'all' else ""
                }
            ]
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, auth=('demofx_bprasath/June-Mahesh', 'start123'))
        response.raise_for_status()
        data = response.json()

        if 'response' in data and data['response'].get('status') == 0:
            items = data['response'].get('data', [])

            if items:
                table_rows = "".join(
                    f"<tr><td>{item.get('sku', 'N/A')}</td><td>{item.get('label', 'N/A')}</td><td>{item.get('attribute21', 'N/A')}</td><td>{item.get('attribute19', 'N/A')}</td><td>{item.get('attribute10', 'N/A')}</td><td>{item.get('attribute11', 'N/A')}</td><td>{item.get('attribute12', 'N/A')}</td><td>{item.get('attribute13', 'N/A')}</td></tr>"
                    for item in items
                )
                has_next = len(items) == items_per_page
            else:
                table_rows = "<tr><td colspan='8'>No Data Available</td></tr>"
                has_next = False
        else:
            table_rows = "<tr><td colspan='8'>No Data Available</td></tr>"
            has_next = False

        has_previous = page > 1

        return render_template(
            "index.html",
            table_rows=table_rows,
            column=column,
            value=value,
            page=page,
            has_next=has_next,
            has_previous=has_previous
        )
    except requests.exceptions.Timeout:
        return render_template("index.html", error_message="Request Timeout")
    except requests.exceptions.RequestException as e:
        return render_template("index.html", error_message=str(e))

if __name__ == "__main__":
    app.run(debug=True)
