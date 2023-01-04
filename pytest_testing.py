import pytest
import requests


class Test():
    def test_get_product(self):
        response = requests.get("https://ggj9bsyiof.execute-api.us-west-2.amazonaws.com/prod/product")
        assert response.status_code == 200
