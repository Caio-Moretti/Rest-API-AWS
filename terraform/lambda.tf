data "archive_file" "serverless_api_artefact" {
  output_path = "files/serverless-api-artefact.zip"
  type        = "zip"
  source_file = "${path.module}/lambdas/serverless-api/lambda_function.py"
}

resource "aws_lambda_function" "serverless-api" {
  function_name = "lambda_function"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"

  filename         = data.archive_file.serverless_api_artefact.output_path
  source_code_hash = data.archive_file.serverless_api_artefact.output_base64sha256

  timeout     = 5
  memory_size = 128
}