import os
import boto3

from airflow import settings
from airflow.models import Connection
from dotenv import load_dotenv, dotenv_values

load_dotenv()


os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '/home/.aws/credentials'
session = boto3.Session()
credentials = session.get_credentials()

if credentials is None:
    raise ValueError("AWS credentials not found. Ensure they are set in your environment or AWS credentials file.")

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
aws_config = dotenv_values(f"{AIRFLOW_HOME}dags/aws_config.env")

# aws config constants
AWS_ACCESS_KEY = credentials.access_key
AWS_SECRET_KEY = credentials.secret_key
AWS_REGION = aws_config['region']
REDSHIFT_USER = aws_config['redshift_user']
REDSHIFT_PASSWORD = aws_config['redshift_password']
REDSHIFT_DB = aws_config['redshift_db']
REDSHIFT_HOST = aws_config['redshift_endpoint'].split(":")[0]
REDSHIFT_PORT = aws_config['redshift_port']

def create_airflow_connections():
    session = settings.Session()
    
    # AWS Connection
    aws_conn = Connection(
        conn_id="aws_default",
        conn_type="aws",
        login=AWS_ACCESS_KEY,
        password=AWS_SECRET_KEY,
        extra={
            "region_name": AWS_REGION
        }
    )

    # Redshift Connection
    redshift_conn = Connection(
        conn_id="redshift_default",
        conn_type="postgres",
        host=REDSHIFT_HOST,
        login=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD,
        port=REDSHIFT_PORT,
        schema=REDSHIFT_DB
    )

    session.add(aws_conn)
    session.add(redshift_conn)
    session.commit()
