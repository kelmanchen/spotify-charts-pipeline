variable "aws_region" {
  description = "Region for the AWS services to run in."
  type        = string
  default     = "ap-southeast-2"
}

variable "bucket_prefix" {
  description = "Spotify S3 Bucket Name"
  type        = string
  default     = "spotify-data-"
}

variable "redshift_master_username" {
  default = "admin"
  description = "The master username for the Redshift cluster"
}
