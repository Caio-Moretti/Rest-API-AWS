import boto3
import requests


url = "https://ggj9bsyiof.execute-api.us-west-2.amazonaws.com/prod/product"

payload = {"productId": "2"}
headers = {"Content-Type": "application/json"}

response = requests.request("GET", url, json=payload, headers=headers)

print(response.text)


#
# dynamodb = boto3.resource('dynamodb')
# productId = '1'
# table = dynamodb.Table('product-inventory')
#
# table.put_item(
#     Item={
#         'productId': '1',
#         'Name': 'teste1'
#     }
# )
# print('done')



