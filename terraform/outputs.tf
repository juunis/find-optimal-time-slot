output "api_url" {
  description = "Base URL for the API"
  value       = "${aws_api_gateway_stage.stage.invoke_url}/api/v1/meetings/optimize"
}

output "lambda_name" {
  value = aws_lambda_function.lambda.function_name
}
