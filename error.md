O que eu quero fazer? Usar a função get product by id
na tabela product-inventory

então essa função é usada:
```python
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
```

essa função usa o get_item do boto3 e preenche uma variável chamada response
com o get_item usando o Id especificado no request.
O formato correto que o boto3 traz é um json em que a primeira chave é
"Items": que retorna o dicionário do item requerido pelo Id.
Então o código usa usa o response['Items'] como o parâmetro body da função buildResponse.
a função buildResponse é usada nessa função getProduct pra retornar o produto desejado em um formato
de dicionário (JSON)

Função buildResponse:
```python
def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,  # o Problema do get by ID provavelmente está na cosntrução do response nessa função
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response, response['body']
```

Essa função cria uma variável local chamada response que tem algumas chaves necessárias no request,
e então cria uma chave chamada response['body'] e atribui o body recebido a ela (no caso do getProduct é
o response['Items'] vindo do table.get_item())

Porém, vendo os logs do CloudWatch da pra ver que existe um erro de 'NoneType', que eu acho que significa
que o response vindo do table.get_item() não tem o response['Items'], e quando o getProduct() tenta acessar
essa chave, da esse erro porque ela não existe.

Isso nos leva então ao cadastro do produto que é a função saveProduct() abaixo:
```python
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
        logger.exception('Error at saveProduct function')
```

quando essa função é chamada ela recebe um requestBody do request que é o json que vai ser colocado na tabela
do dynamodb no método HTTP Post. então ele pega esse item e faz um simples table.put_item(Item=requestBody) e
cria esse produto na tabela.
Porém se nós olharmos em um outro arquivo usando o boto3, esse item que foi criado não tem mesmo a chave 'Items'
como podemos ver a seguir:
código de get_item() do boto3 conectado a tabela do dynamodb:
````python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('product-inventory')

response = table.get_item(
    Key={
        'productId': "3"
    }
)

if 'Items' in response:
    print(response['Item'])
else:
    print(response)
````

response que chega do get_item():
````json
{
  'ResponseMetadata': {
    'RequestId': '63CNS33GBKBQNL2POSEMDJ8U4RVV4KQNSO5AEMVJF66Q9ASUAAJG',
    'HTTPStatusCode': 200,
    'HTTPHeaders': {
      'server': 'Server',
      'date': 'Fri, 06 Jan 2023 17:17:54 GMT',
      'content-type': 'application/x-amz-json-1.0',
      'content-length': '2',
      'connection': 'keep-alive',
      'x-amzn-requestid': '63CNS33GBKBQNL2POSEMDJ8U4RVV4KQNSO5AEMVJF66Q9ASUAAJG',
      'x-amz-crc32': '2745614147'
    },
    'RetryAttempts': 0
  }
}
````

O mais estranho é que se criarmos uma tabela pelo boto3 (a minha foi criada pelo Terraform)
e colocarmos um item nela dessa forma:
`````python
table = dynamodb.create_table(
    TableName='todos',
    KeySchema=[
        {
            'AttributeName': 'todo_id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'todo_id',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)
# Wait until the table exists.
print('Creating...')
table.wait_until_exists()

# Print out some data about the table.
print(table.item_count)

table.put_item(
    TableName='product-inventory',
    Item={
        'productId': '2',
        'Name': 'teste2'
    }
)
`````

e depois usarmos o get_item() do boto3 nesse item que foi colocado da mesma forma que na
lambda, esse é o resultado que recebemos como response:
