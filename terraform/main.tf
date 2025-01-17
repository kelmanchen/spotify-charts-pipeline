terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "spotify-data-bucket" {
  bucket_prefix = var.bucket_prefix
  force_destroy = true
}
