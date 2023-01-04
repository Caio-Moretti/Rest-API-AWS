resource "aws_dynamodb_table" "product-inventory-table" {
  name         = "product-inventory"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "productId"

  attribute {
    name = "productId"
    type = "S"
  }
}
