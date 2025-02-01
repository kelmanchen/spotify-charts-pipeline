import os
import boto3
import logging

from dotenv import load_dotenv, dotenv_values
from botocore.exceptions import NoCredentialsError

# Configure Logging
logging.basicConfig(
    filename="chart_scraper_log.log",
    level=logging.INFO
)

load_dotenv()

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '/home/.aws/credentials'

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
CSV_PATH = f'{AIRFLOW_HOME}data/'
aws_config = dotenv_values(f"{AIRFLOW_HOME}dags/aws_config.env")

S3_BUCKET_NAME = aws_config['bucket_name']

def upload_csv_s3(files):
    try:
        s3 = boto3.resource("s3")
    except NoCredentialsError as e:
        logging.error(f"No credentials error: {e}")
        raise

    for file in files:
        try:
            s3.meta.client.upload_file(Filename=f'{CSV_PATH}{file}', Bucket=S3_BUCKET_NAME, Key=file)
            logging.info(f"Succesfully uploaded {CSV_PATH}{file} to S3://{S3_BUCKET_NAME}")
        except Exception as e:
            logging.error(f"Failed to upload {CSV_PATH}{file} to S3: {e}")
            raise

