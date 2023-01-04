locals {
  lambdas = {
    get = {
      description = "Get products"
      memory      = 256
      timeout     = 10
    }
    delete = {
      description = "Delete given product"
      memory      = 128
      timeout     = 5
    }
    put = {
      description = "Update given product"
      memory      = 128
      timeout     = 5
    }
    post = {
      description = "Create new product"
      memory      = 128
      timeout     = 5
    }
  }
}