variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
}

variable "couples_table_name" {
  description = "Name of the DynamoDB couples table"
  type        = string
}

variable "rsvp_table_name" {
  description = "Name of the DynamoDB RSVP responses table"
  type        = string
}

variable "docker_image" {
  description = "Docker image for the RSVP web application"
  type        = string
}

variable "ngrok_custom_domain" {
  description = "Your static free ngrok domain"
  type        = string
}