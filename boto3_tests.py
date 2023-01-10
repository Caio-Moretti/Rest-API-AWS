import boto3
#
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('product-inventory')

response = table.get_item(
    Key={
        'productId': "3"
    }
)

if 'Items' in response:
    print(response['Items'])
else:
    print(response)


table.put_item(
    TableName='product-inventory',
    Item={
        'productId': '2',
        'Name': 'teste2'
    }
)
# print('done')


table = dynamodb.Table('todos')


response = table.get_item(
    Key={
        'todo_id': '1',
    }
)
item = response['Item']
print(item)
print()
print(response)

# table = dynamodb.create_table(
#     TableName='todos',
#     KeySchema=[
#         {
#             'AttributeName': 'todo_id',
#             'KeyType': 'HASH'
#         }
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'todo_id',
#             'AttributeType': 'S'
#         }
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 5,
#         'WriteCapacityUnits': 5
#     }
# )
# # Wait until the table exists.
# print('Creating...')
# table.wait_until_exists()
#
# # Print out some data about the table.
# print(table.item_count)


