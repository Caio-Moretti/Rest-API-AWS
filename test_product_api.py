# TODO criar mensagens personalizadas para as famílias de status code
#  dos erros da API pra melhorar os testes

import json
import os
import uuid

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
    # post product
    post_product_payload = new_product_paylaod()
    post_product_response = create_product(post_product_payload)
    assert post_product_response.status_code == 200

    post_product_data = post_product_response.json()
    product_id = post_product_data['Item']['productId']
    product_id_payload = {
        "productId": product_id
    }
    get_product_response = get_product(product_id_payload)
    assert get_product_response.status_code == 200
    get_product_data = get_product_response.json()
    assert get_product_data['productId'] == post_product_payload["productId"]
    assert get_product_data['productName'] == post_product_payload['productName']

    delete_product(product_id_payload)


def test_can_update_product():
    # create a product
    post_product_payload = new_product_paylaod()
    post_product_response = create_product(post_product_payload)
    assert post_product_response.status_code == 200

    # update the produtct created
    update_payload = {
        "productId": post_product_payload["productId"],
        "updateKey": "productName",
        "updateValue": "mudou"
    }

    update_product_response = update_product(update_payload)
    assert update_product_response.status_code == 200

    # get and validate the changes
    product_id_payload = {
        "productId": update_payload["productId"]
    }
    get_product_response = get_product(product_id_payload)

    assert get_product_response.status_code == 200
    get_product_data = get_product_response.json()

    assert get_product_data["productId"] == update_payload["productId"]
    assert get_product_data["productName"] == update_payload["updateValue"]

    delete_product(product_id_payload)


def test_can_list_products():
    # create N tasks.
    n = 3
    for _ in range(n):
        post_product_payload = new_product_paylaod()
        post_product_response = create_product(post_product_payload)
        assert post_product_response.status_code == 200

    # list tasks and check that there are N items
    get_products_response = get_products()
    assert get_products_response.status_code == 200
    get_products_data = get_products_response.json()

    products = get_products_data['products']
    assert len(products) == n

    for lits_item in products:
        for key, value in lits_item.items():
            if key == 'productId':
                product_id_payload = {
                    'productId': value
                }
                delete_product(product_id_payload)
            else:
                pass


def test_can_delete_product():
    # post product
    post_product_payload = new_product_paylaod()
    post_product_response = create_product(post_product_payload)
    assert post_product_response.status_code == 200

    post_product_data = post_product_response.json()
    product_id = post_product_data['Item']['productId']

    product_id_payload = {
        'productId': product_id
    }

    # delete a product
    delete_product_response = delete_product(product_id_payload)
    assert delete_product_response.status_code == 200

    # get the product and check that it's not found.
    get_product_response = get_product(product_id)
    assert get_product_response.status_code != 200


def create_product(payload):
    return requests.post(f"{endpoint}/product", json=payload)


def get_product(product_id_payload):
    return requests.get(f"{endpoint}/product", json=product_id_payload)


def get_products():
    return requests.get(f"{endpoint}/products")


def update_product(payload):
    return requests.patch(f"{endpoint}/product", json=payload)


def delete_product(product_id_payload):
    return requests.delete(f"{endpoint}/product", json=product_id_payload)


def new_product_paylaod():
    product_id = f"product_id_{uuid.uuid4().hex}"
    product_name = f"product_name_{uuid.uuid4().hex}"

    # print(f"Creating product id: {product_id} with product name: {product_name}")

    return {
        "productId": product_id,
        "productName": product_name
    }
