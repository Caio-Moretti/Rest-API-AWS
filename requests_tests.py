import requests
import json
import os

with open(os.path.join("terraform", "terraform.tfstate"), "r") as file:
    tfstate_json = json.loads(file.read())

endpoint = f"{tfstate_json['outputs']['api_url']['value']}prod"
print(f" API URL: {endpoint}")

product_id_payload = {
    "productId": "1"
}

response = requests.get(f"{endpoint}/product", json=product_id_payload)

print(response.text)
print(response.status_code)
