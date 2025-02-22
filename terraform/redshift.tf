#  random password / suffix

resource "random_password" "password" {
  length           = 16
  special          = false
  min_lower        = 1
  min_upper        = 1
  min_numeric      = 1
}

resource "random_string" "unique_suffix" {
  length  = 6
  special = false
}

# redshift

resource "aws_redshift_cluster" "spotify_data_cluster" {
  cluster_identifier = "spotify-redshift-cluster"
  database_name      = "spotify_songs_data"
  master_username    = var.redshift_master_username
  master_password    = random_password.password.result
  node_type          = "dc2.large"
  cluster_type       = "single-node"

  skip_final_snapshot = true
}

resource "aws_secretsmanager_secret" "redshift_connection" {
  description = "Redshift connect details"
  name        = "spotify-redshift-secret-${random_string.unique_suffix.result}"
}

resource "aws_secretsmanager_secret_version" "redshift_connection" {
  secret_id = aws_secretsmanager_secret.redshift_connection.id
  secret_string = jsonencode({
    username            = aws_redshift_cluster.spotify_data_cluster.master_username
    password            = aws_redshift_cluster.spotify_data_cluster.master_password
    engine              = "redshift"
    host                = aws_redshift_cluster.spotify_data_cluster.endpoint
    port                = "5439"
    dbClusterIdentifier = aws_redshift_cluster.spotify_data_cluster.cluster_identifier
  })
}
