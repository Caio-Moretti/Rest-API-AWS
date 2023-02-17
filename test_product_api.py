import json
import os
import uuid
import pytest
import requests

with open(os.path.join("terraform", "terraform.tfstate"), "r") as file:
    tfstate_json = json.loads(file.read())

endpoint = f"{tfstate_json['outputs']['api_url']['value']}prod"
print(f" API URL: {endpoint}")


@pytest.fixture()
def setup(request):
    product_id = f"product_id_{uuid.uuid4().hex}"
    product_name = f"product_name_{uuid.uuid4().hex}"

    payload = {
        "productId": product_id,
        "productName": product_name
    }

    response = requests.post(f"{endpoint}/product", json=payload)

    # delete product created
    def delete_created_product():
        requests.delete(f"{endpoint}/product", json={"productId": payload["productId"]})

    request.addfinalizer(delete_created_product)

    return response, payload  # retorna o response e o payload do post


@pytest.fixture()
def create_initial_product():
    # creating product
    product_id = f"product_id_{uuid.uuid4().hex}"
    product_name = f"product_name_{uuid.uuid4().hex}"

    payload = {
        "productId": product_id,
        "productName": product_name
    }

    response = requests.post(f"{endpoint}/product", json=payload)
    assert response.status_code == 201

    # returning product json
    return response.json()


@pytest.fixture
def setup_update(create_initial_product, request):
    # defining a new payload with the updated values
    product_id = create_initial_product["Item"]["productId"]
    updated_payload = {
        "productId": product_id,
        "updateKey": "productName",
        "updateValue": "changed"
    }

    # patching the new values
    response = requests.patch(f"{endpoint}/product", json=updated_payload)
    assert response.status_code == 200

    # deleting product updated
    def delete_updated_product():
        requests.delete(f"{endpoint}/product", json={"productId": product_id})

    request.addfinalizer(delete_updated_product)

    # returning updated product and payload
    return response, updated_payload


# TODO juntar o setup e o setup_update
@pytest.fixture()
def setup_list(request):
    # create N products.
    n = 3  # TODO botar o n como parâmetro
    for _ in range(n):
        # creating product
        product_id = f"product_id_{uuid.uuid4().hex}"
        product_name = f"product_name_{uuid.uuid4().hex}"

        payload = {
            "productId": product_id,
            "productName": product_name
        }

        response = requests.post(f"{endpoint}/product", json=payload)
        assert response.status_code == 201

    get_products_response = requests.get(f"{endpoint}/products")
    products_list = get_products_response.json()
    products = products_list['products']

    def delete_n_products():
        # delete products
        for lits_item in products:
            for key, value in lits_item.items():
                if key == 'productId':
                    product_id_payload = {
                        'productId': value
                    }
                    requests.delete(f"{endpoint}/product", json=product_id_payload)
                else:
                    pass

    request.addfinalizer(delete_n_products)
    return n, products


def test_01_verify_endpoint_health():
    # enter the /health path and get the 200 OK status code
    response = requests.get(f"{endpoint}/health")
    assert response.status_code == 200


def test_02_verify_product_creation(setup):
    # create product
    response, payload = setup
    assert response.status_code in [200, 201]

    # validate creation
    product = response.json()
    assert payload['productId'] == product['Item']['productId']
    assert payload['productName'] == response.json()['Item']['productName']


def test_03_verify_product_update(setup_update):
    # using the fixture to create, update ant delete product
    updated_response, updated_payload = setup_update
    assert updated_response.status_code in [200, 201, 204]

    # validate changes
    product_name = updated_response.json()['UpdatedAttributes']['Attributes']["productName"]
    assert product_name == updated_payload["updateValue"]

    # assert product["Item"]["productId"] == updated_payload["productId"]
    # TODO mudar o response no lambda pra retornar o ID


def test_04_verify_products_list(setup_list):
    # setting up the test from fixture and getting the number of created products and length of the products list
    number_expected, products = setup_list
    products_length = len(products)

    # asserting that the number of created items equals the length of products
    assert products_length == number_expected


def test_05_verify_product_deletion(setup):
    # Extrai a resposta e o payload da fixture setup
    response, payload = setup

    # Verifica se a resposta do POST foi bem-sucedida
    assert response.status_code == 201

    # Faz a chamada para deletar o produto
    delete_response = requests.delete(f"{endpoint}/product", json={"productId": payload["productId"]})

    # Verifica se a resposta do DELETE foi bem-sucedida
    assert delete_response.status_code == 200

    # Verifica se o produto foi realmente deletado
    get_response = requests.get(f"{endpoint}/product", json={"productId": payload["productId"]})
    assert get_response.status_code == 404
