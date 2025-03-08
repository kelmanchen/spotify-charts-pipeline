import boto3
import logging

from botocore.exceptions import NoCredentialsError

# Configure Logging
logging.basicConfig(
    filename="chart_scraper_log.log",
    level=logging.INFO
)

def upload_csv_s3(files, csv_path, s3_bucket_name):
    try:
        s3 = boto3.resource("s3")
    except NoCredentialsError as e:
        logging.error(f"No credentials error: {e}")
        raise

    for file in files:
        try:
            s3.meta.client.upload_file(Filename=f'{csv_path}{file}', Bucket=s3_bucket_name, Key=file)
            logging.info(f"Succesfully uploaded {csv_path}{file} to S3://{s3_bucket_name}")
        except Exception as e:
            logging.error(f"Failed to upload {csv_path}{file} to S3: {e}")
            raise

