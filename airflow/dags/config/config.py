import os
import boto3

from dotenv import load_dotenv, dotenv_values

load_dotenv()

# get AWS credentials
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '/home/.aws/credentials'

session = boto3.Session()
credentials = session.get_credentials()

if credentials is None:
    raise ValueError("AWS credentials not found. Ensure they are set in your environment or AWS credentials file.")

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")
AWS_CONFIG = dotenv_values(f"{AIRFLOW_HOME}dags/config/aws_config.env")

CONFIG = {
    "SPOTIFY_TOKEN": os.getenv("SPOTIFY_ACCESS_TOKEN"),
    "EXTRACT_START_DATE": os.getenv("EXTRACT_START_DATE"),
    "EXTRACT_END_DATE": os.getenv("EXTRACT_END_DATE"),
    "AIRFLOW_HOME": AIRFLOW_HOME,
    "AWS": {
        "ACCESS_KEY": credentials.access_key,
        "SECRET_KEY": credentials.secret_key,
        "S3_BUCKET_NAME": AWS_CONFIG["bucket_name"],
        "REGION": AWS_CONFIG["region"],
        "REDSHIFT_CLUSTER_ID": AWS_CONFIG["redshift_cluster_id"],
        "REDSHIFT_USER": AWS_CONFIG["redshift_user"],
        "REDSHIFT_PASSWORD": AWS_CONFIG["redshift_password"],
        "REDSHIFT_DB": AWS_CONFIG["redshift_db"],
        "REDSHIFT_HOST": AWS_CONFIG["redshift_endpoint"].split(":")[0],
        "REDSHIFT_PORT": AWS_CONFIG["redshift_port"]
    },
    "CSV_PATH": f"{AIRFLOW_HOME}data/",
    "SQL_PATH": f"{AIRFLOW_HOME}dags/sql/",
    "DBT": {
        "DBT_PROJECT_PATH": f'{AIRFLOW_HOME}dags/dbt',
        "DBT_EXECUTABLE_PATH": f'{AIRFLOW_HOME}dbt_venv/bin/dbt'
    }
}

