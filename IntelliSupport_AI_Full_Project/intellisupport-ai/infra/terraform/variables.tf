variable "aws_region" { type=string default="ap-south-1" }
variable "project_name" { type=string default="intellisupport-ai" }
variable "db_password" { type=string sensitive=true }
variable "container_image" { type=string description="ECR image URI including tag" }
