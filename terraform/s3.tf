resource "aws_s3_bucket" "spotify-data-bucket" {
  bucket_prefix = var.bucket_prefix
  force_destroy = true
}
