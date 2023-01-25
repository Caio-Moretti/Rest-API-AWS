import boto3
import json
import logging
from decimal import Decimal

logger = logging.getLogger()

dynamodb_table_name = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table_name)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'

healthPath = '/health'
productPath = '/product'
productsPath = '/products'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']

    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)

    elif httpMethod == getMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = getProduct(requestBody['productId'])

    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()

    elif httpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body']))

    elif httpMethod == patchMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = modifyProduct(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue'])

    elif httpMethod == deleteMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = deleteProduct(requestBody['productId'])

    else:
        response = buildResponse(404, 'Not Found')

    return response


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

        return json.JSONEncoder.default(self, obj)


def getProduct(productId):
    try:
        response = table.get_item(
            Key={
                'productId': productId
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': f'productId: {productId} not found'})
    except:
        logger.exception('(Error) did not execute the try')


def getProducts():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body = {
            'products': result
        }

        return buildResponse(200, body)

    except:
        logger.exception('Error')


def saveProduct(requestBody):
    try:
        # get item with productId
        response = table.get_item(
            Key={
                'productId': requestBody["productId"]
            }
        )
        # checks if the ID already exists
        if 'Item' in response:
            return buildResponse(409, {'Message': f'productId: {requestBody["productId"]} already exists'})

        # creates if it doesn't exist
        else:
            table.put_item(Item=requestBody)
            body = {
                'Operation': 'SAVE',
                'Message': 'SUCCESS',
                'Item': requestBody
            }
            return buildResponse(201, body)
    except:
        logger.exception('Error at saveProduct function')


def modifyProduct(productId, updateKey, updateValue):
    try:
        # get item with productId
        response_get = table.get_item(
            Key={
                'productId': productId
            }
        )

        # checks if the productId exists
        if 'Item' in response_get:
            response_update = table.update_item(
                Key={
                    'productId': productId
                },
                UpdateExpression=f'set {updateKey} = :value',
                ExpressionAttributeValues={
                    ':value': updateValue
                },
                ReturnValues='UPDATED_NEW'
            )
            body = {
                'Operation': 'UPDATE',
                'Message': 'SUCCESS',
                'UpdatedAttributes': response_update
            }
            return buildResponse(200, body)

        # 404 if it doesn't exist
        else:
            return buildResponse(404, {'Message': f'productId: {productId} not found'})
    except:
        logger.exception('Error')


def deleteProduct(productId):
    try:
        response_get = table.get_item(
            Key={
                'productId': productId
            }
        )
        if 'Item' in response_get:
            response_delete = table.delete_item(
                Key={
                    'productId': productId
                },
                ReturnValues='ALL_OLD'
            )
            body = {
                'Operation': 'DELETE',
                'Message': 'SUCCESS',
                'deletedItem': response_delete
            }
            return buildResponse(200, body)
        else:
            return buildResponse(404, {'Message': f'productId: {productId} not found'})
    except:
        logger.exception('Error')


def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    print(body)
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response
