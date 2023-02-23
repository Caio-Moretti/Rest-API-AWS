import json
import os
import uuid
import pytest
import requests

# gets endpoint
with open(os.path.join("terraform", "terraform.tfstate"), "r") as file:
    tfstate_json = json.loads(file.read())

endpoint = f"{tfstate_json['outputs']['api_url']['value']}prod"


@pytest.fixture()
def products(request):
    # saves the product ids passed
    product_ids = []

    # number of products to be created as parameter
    n = request.param.get("n")

    # creating n products
    for i in range(n):
        product_id = f"product_id_{uuid.uuid4().hex}"
        product_name = f"product_name_{uuid.uuid4().hex}"

        payload = {
            "productId": product_id,
            "productName": product_name
        }

        response = requests.post(f"{endpoint}/product", json=payload)
        assert response.status_code == 201

        product_ids.append(product_id)

    # getting the products
    products = requests.get(f"{endpoint}/products").json()["products"]

    # defining the finalizer to delete all products
    def delete_all_products():
        for item in product_ids:
            requests.delete(f"{endpoint}/product", json={"productId": item})

    # register finalizer
    request.addfinalizer(delete_all_products)

    # return products list and products ids
    return products, product_ids


def test_01_verify_endpoint_health():
    # enter the /health path and get the 200 OK status code
    response = requests.get(f"{endpoint}/health")
    assert response.status_code == 200


@pytest.mark.parametrize("products", [{"n": 2}], indirect=True)
def test_02_verify_product_creation(products):
    # gets product ids passed in payload and products list
    products_list, product_ids = products

    # checks if products list ids equals product ids from payload
    assert set(product_ids) == set(product['productId'] for product in products_list)


@pytest.mark.parametrize("products", [{"n": 1}], indirect=True)
def test_03_verify_product_update(products):
    # gets product ids passed in payload and products list
    products_list, product_ids = products

    # updates the created product and checks if it's really changed
    update_payload = {
        "productId": product_ids[0],
        "updateKey": "productName",
        "updateValue": "changed"
    }
    response = requests.patch(f"{endpoint}/product", json=update_payload)
    assert response.status_code == 200

    products_updated = requests.get(f"{endpoint}/products").json()["products"]
    assert products_updated[0]["productName"] == "changed" != products_list[0]["productName"]


@pytest.mark.parametrize("products", [{"n": 3}], indirect=True)
def test_04_verify_products_list(products):
    # checks if the list size equals the number of products passed as parameter to create
    assert len(products[0]) == 3


@pytest.mark.parametrize("products", [{"n": 1}], indirect=True)
def test_05_verify_product_deletion(products):
    # deletes product created and checks if the product was deleted
    response_deletion = requests.delete(f"{endpoint}/product", json={"productId": products[0][0]["productId"]})
    assert response_deletion.status_code == 200

    response = requests.get(f"{endpoint}/product", json={"productId": products[0][0]["productId"]})
    assert response.status_code == 404
