variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  default     = "find-optimal-time-slot"
}

variable "lambda_handler" {
  description = "Lambda function handler"
  default     = "optimal_time_slot_lambda.lambda_handler"
}

variable "lambda_zip_file" {
  description = "Path to the zipped Lambda code"
  default     = "../optimal_time_slot_lambda/dist/lambda.zip"
}

variable "api_gateway_api_name" {
  description = "Name of the API Gateway REST API"
  default     = "find-optimal-time-slot-api"
}