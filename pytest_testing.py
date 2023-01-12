import json
import os
import pytest
import requests

with open(os.path.join("terraform", "terraform.tfstate"), "r") as file:
    tfstate_json = json.loads(file.read())

api_url = tfstate_json['outputs']['api_url']['value']
print(api_url)

# class Test():
#     def test_get_product(self):
#         response = requests.get(api_url)
#         assert response.status_code == 200
