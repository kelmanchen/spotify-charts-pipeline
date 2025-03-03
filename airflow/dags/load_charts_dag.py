import os
import datetime as dt

from dotenv import load_dotenv, dotenv_values
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from cosmos import DbtTaskGroup, ProfileConfig, ProjectConfig, ExecutionConfig
from cosmos.profiles import RedshiftUserPasswordProfileMapping
from extract_data import get_all_chart_data
from upload_to_s3 import upload_csv_s3
from airflow_connections import create_airflow_connections

load_dotenv()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1
}

# constants
EXT_START_DATE = dt.datetime(2020, 1, 1)
EXT_END_DATE = dt.datetime(2024, 12, 31)
SPOTIFY_TOKEN = os.getenv('SPOTIFY_ACCESS_TOKEN')
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
CSV_PATH = f'{AIRFLOW_HOME}data/'

# aws variables
aws_config = dotenv_values(f"{AIRFLOW_HOME}dags/aws_config.env")
S3_BUCKET_NAME = aws_config['bucket_name']
REDSHIFT_DB = aws_config['redshift_db']
REDSHIFT_CLUSTER_ID = aws_config['redshift_cluster_id']

# Table profiles mapping
table_profiles = {
    'artists': {
        'upsert_keys': ["artist_id"],
        'file_type': ["csv"]
    },
    'chart_data': {
        'upsert_keys': ["track_id", "entry_date"],
        'file_type': ["csv", "DELIMITER AS ','", "DATEFORMAT 'YYYY-MM-DD'", "IGNOREHEADER 1"]
    },
    'track_artists': {
        'upsert_keys': ["track_id", "artist_id"],
        'file_type': ["csv"]
    },
    'tracks': {
        'upsert_keys': ["track_id"],
        'file_type': ["csv"]
    }
}

# dbt profile
DBT_PROJECT_PATH = f'{AIRFLOW_HOME}dags/dbt'
DBT_EXECUTABLE_PATH = f'{AIRFLOW_HOME}dbt_venv/bin/dbt'

profile_config = ProfileConfig(
    profile_name = "default",
    target_name = "dev",
    profile_mapping = RedshiftUserPasswordProfileMapping(
        conn_id = "redshift_default",
        profile_args = {
            "schema": "public"
        }
    )
)

execution_config = ExecutionConfig(
    dbt_executable_path = DBT_EXECUTABLE_PATH,
)

with DAG(
    dag_id=f"load_charts_dag",
    default_args=default_args,
    description=f"Load and upload charts data to S3",
    schedule_interval=None,
    catchup=False,
    tags=['spotify']
) as dag:
    setup_connections = PythonOperator(
        task_id="setup_airflow_connections",
        python_callable=create_airflow_connections
    )

    get_charts_data = PythonOperator(
        task_id = "extract_spotify_charts",
        python_callable = get_all_chart_data,
        op_kwargs = {
            'token': SPOTIFY_TOKEN,
            'start_date': EXT_START_DATE,
            'end_date': EXT_END_DATE,
            'csv_url': CSV_PATH
        },
        trigger_rule="dummy"
    )

    upload_csv_to_s3 = PythonOperator(
        task_id = "upload_csv_to_s3",
        python_callable = upload_csv_s3,
        op_kwargs = {
            'files': [f"{table}.csv" for table in table_profiles.keys()]
        }
    )

    create_redshift_tables = RedshiftDataOperator(
        task_id = "create_redshift_tables",
        database = REDSHIFT_DB,
        sql = open(f"{AIRFLOW_HOME}dags/create_tables.sql").read(),
        cluster_identifier = REDSHIFT_CLUSTER_ID,
        workgroup_name=None
    )

    with TaskGroup("transfer_s3_to_redshift") as transfer_s3_to_redshift:
        for table_name, profile in table_profiles.items():
            S3ToRedshiftOperator(
                task_id = f"transfer_{table_name}_s3_to_redshift",
                s3_bucket = S3_BUCKET_NAME,
                s3_key = f"{table_name}.csv",
                schema = "PUBLIC",
                table = table_name,
                copy_options = profile['file_type'],
                method = "UPSERT",
                upsert_keys = profile['upsert_keys']
            )

    dbt_transform = DbtTaskGroup(
        group_id = "dbt_transformations",
        project_config = ProjectConfig(DBT_PROJECT_PATH),
        profile_config = profile_config,
        execution_config = execution_config
    )

    setup_connections >> upload_csv_to_s3 >> create_redshift_tables >> transfer_s3_to_redshift >> dbt_transform


