resource "aws_api_gateway_account" "permissions" {
  cloudwatch_role_arn = aws_iam_role.cloudwatch.arn
}

resource "aws_api_gateway_rest_api" "this" {
  name = "serverless-api-gateway"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "health" {
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "health"
  rest_api_id = aws_api_gateway_rest_api.this.id
}


resource "aws_api_gateway_method" "get_health" {
  authorization    = "NONE"
  http_method      = "GET"
  resource_id      = aws_api_gateway_resource.health.id
  rest_api_id      = aws_api_gateway_rest_api.this.id
  api_key_required = false
}

resource "aws_api_gateway_integration" "integration_get_health" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.health.id
  http_method             = aws_api_gateway_method.get_health.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.serverless-api.invoke_arn
}


resource "aws_api_gateway_resource" "product" {
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "product"
  rest_api_id = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_method" "get_product" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.product.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_integration" "integration_get_product" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.product.id
  http_method             = aws_api_gateway_method.get_product.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.serverless-api.invoke_arn
}

resource "aws_api_gateway_method" "delete_product" {
  authorization = "NONE"
  http_method   = "DELETE"
  resource_id   = aws_api_gateway_resource.product.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_integration" "integration_delete_product" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.product.id
  http_method             = aws_api_gateway_method.delete_product.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.serverless-api.invoke_arn
}

resource "aws_api_gateway_method" "patch_product" {
  authorization = "NONE"
  http_method   = "PATCH"
  resource_id   = aws_api_gateway_resource.product.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_integration" "integration_patch_product" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.product.id
  http_method             = aws_api_gateway_method.patch_product.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.serverless-api.invoke_arn
}

resource "aws_api_gateway_method" "post_product" {
  authorization = "NONE"
  http_method   = "POST"
  resource_id   = aws_api_gateway_resource.product.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_integration" "integration_post_product" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.product.id
  http_method             = aws_api_gateway_method.post_product.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.serverless-api.invoke_arn
}

resource "aws_api_gateway_resource" "products" {
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "products"
  rest_api_id = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_method" "get_products" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.products.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_integration" "integration_get_products" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.products.id
  http_method             = aws_api_gateway_method.get_products.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.serverless-api.invoke_arn
}

resource "aws_api_gateway_deployment" "example" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.this.id))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "example" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
  stage_name    = "prod"
}


resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = aws_api_gateway_stage.example.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowMyDemoAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.serverless-api.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.this.execution_arn}/*/*/*"
}