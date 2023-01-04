import boto3
import json
import logging
from decimal import Decimal

logger = logging.getLogger()

dynamodb_table_name = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table_name)

getMethod = 'GET'  # esse é o método get
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
productPath = '/product'  # get + esse path = get product by id
productsPath = '/products'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)

    elif httpMethod == getMethod and path == productPath:
        response = getProduct(event['queryStringParameters']['productId'])  # erro é nessa linha provavelmente.

    elif httpMethod == getMethod and path == productsPath:
        response = getProducts()

    elif httpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body']))

    elif httpMethod == patchMethod and path == productPath:
        requestBody = json.loads(event['body'])  # talvez esteja dando erro aqui também
        response = modifyProduct(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue'])  # ou aqui

    elif httpMethod == deleteMethod and path == productPath:
        requestBody = json.loads(event['body'])  # mas teria que dar erro aqui também então provavelmente não é
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
        if 'Items' in response:
            return buildResponse(200, response['Items'])  # ou nessa
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
        table.put_item(Item=requestBody)  # não cria o 'Items'
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)

    except:
        logger.exception('Error')


def modifyProduct(productId, updateKey, updateValue):
    try:
        response = table.update_item(
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
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error')


def deleteProduct(productId):
    try:
        response = table.delete_item(
            Key={
                'productId': productId
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
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
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response


