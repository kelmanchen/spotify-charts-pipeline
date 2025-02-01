output "region" {
    description = "AWS Region"
    value = var.aws_region
}

output "bucket_name" {
    description = "S3 bucket name"
    value = aws_s3_bucket.spotify-data-bucket.id
}

output "redshift_user" {
    description = "Redshift cluster username"
    value = aws_redshift_cluster.spotify_data_cluster.master_username
}

output "redshift_password" {
    description = "Redshift cluster password"
    value = aws_redshift_cluster.spotify_data_cluster.master_password
    sensitive = true
}