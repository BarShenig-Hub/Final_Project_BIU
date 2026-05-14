terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
     }
  }
}


provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "myRSVP"

  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]

  manage_default_security_group = true
  default_security_group_ingress = [
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      description = "Allow HTTP"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "Allow SSH"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
  default_security_group_egress = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags = {
    Owner = "RSVP"
    Environment = "dev"
  }
}

resource "aws_dynamodb_table" "rsvp_table" {
  name         = "RSVP"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "phone"

  attribute {
    name = "phone"
    type = "S" # S = String
  }

  tags = {
    Description = "Create DynamoDB table RSVP"
  }
}
resource "aws_instance" "rsvp_web" {
  ami                         = "ami-0c7217cdde317cfec" # Amazon Linux 2023 in us-east-1
  instance_type               = "t2.micro"
  subnet_id                   = module.vpc.public_subnets[0]
  vpc_security_group_ids      = [module.vpc.default_security_group_id]
  associate_public_ip_address = true

  user_data = <<-EOF
          #!/bin/bash

          sudo apt-get update -y
          sudo apt-get install -y docker.io

          systemctl start docker
          systemctl enable docker
# Change the image #
          sudo docker pull barshenig/rsvp-web-app:latest
          sudo docker run -d -p 80:5000 --restart always barshenig/rsvp-web-app:latest
          EOF

  tags = {
    Name = "RSVP-Web-Server"
  }
}

output "website_address" {
  value = "http://${aws_instance.rsvp_web.public_ip}"
}