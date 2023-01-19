# TODO criar mensagens personalizadas para as famílias de status code
#  dos erros da API pra melhorar os testes

import json
import os
# import pytest
import requests

with open(os.path.join("terraform", "terraform.tfstate"), "r") as file:
    tfstate_json = json.loads(file.read())

endpoint = f"{tfstate_json['outputs']['api_url']['value']}prod"
print(f" API URL: {endpoint}")


def test_can_call_endponint():
    response = requests.get(f"{endpoint}/health")
    assert response.status_code == 200


def test_can_create_product():
    post_product_payload = {
        "productId": "1",
        "productName": "new product"
    }
    post_product_response = requests.post(f"{endpoint}/product", json=post_product_payload)
    assert post_product_response.status_code == 200

    post_product_data = post_product_response.json()
    print(post_product_data)

    product_id = post_product_data['Item']['productId']
    get_payload = {
        "productId": product_id
    }
    get_product_response = requests.get(f"{endpoint}/product", json=get_payload)
    assert get_product_response.status_code == 200
    get_product_data = get_product_response.json()
    assert get_product_data['productId'] == post_product_payload["productId"]
    assert get_product_data['productName'] == post_product_payload['productName']

