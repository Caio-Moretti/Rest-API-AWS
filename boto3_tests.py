import boto3

dynamodb_table_name = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table_name)

productId = "3"

response = table.delete_item(
    Key={
        'productId': productId
    },
    ReturnValues='ALL_OLD'
)

print(response)
