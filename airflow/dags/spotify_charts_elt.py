from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from cosmos import DbtTaskGroup, ProfileConfig, ProjectConfig, ExecutionConfig
from cosmos.profiles import RedshiftUserPasswordProfileMapping

# import custom functions
from config.config import CONFIG
from tasks.extract_data import get_all_chart_data
from tasks.upload_to_s3 import upload_csv_s3
from tasks.airflow_connections import create_airflow_connections

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "retries": 2
}

# Table profiles mapping
table_profiles = {
    "artists": {
        "upsert_keys": ["artist_id"],
        "file_type": ["csv"]
    },
    "chart_data": {
        "upsert_keys": ["track_id", "entry_date"],
        "file_type": ["csv", "DELIMITER AS ","", "DATEFORMAT 'YYYY-MM-DD'", "IGNOREHEADER 1"]
    },
    "track_artists": {
        "upsert_keys": ["track_id", "artist_id"],
        "file_type": ["csv"]
    },
    "tracks": {
        "upsert_keys": ["track_id"],
        "file_type": ["csv"]
    }
}

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
    dbt_executable_path = CONFIG["DBT"]["DBT_EXECUTABLE_PATH"],
)

with DAG(
    dag_id=f"spotify_charts_elt",
    default_args=default_args,
    description=f"Load and upload charts data to S3",
    schedule_interval=None,
    catchup=False,
    tags=["spotify"]
) as dag:
    setup_connections = PythonOperator(
        task_id="setup_airflow_connections",
        python_callable=create_airflow_connections,
        op_kwargs = {
            "access_key": CONFIG["AWS"]["ACCESS_KEY"], 
            "secret_key": CONFIG["AWS"]["SECRET_KEY"], 
            "region": CONFIG["AWS"]["REGION"], 
            "redshift_user": CONFIG["AWS"]["REDSHIFT_USER"], 
            "redshift_password": CONFIG["AWS"]["REDSHIFT_PASSWORD"], 
            "redshift_db": CONFIG["AWS"]["REDSHIFT_DB"], 
            "redshift_host": CONFIG["AWS"]["REDSHIFT_HOST"], 
            "redshift_port": CONFIG["AWS"]["REDSHIFT_PORT"]
        }
    )

    get_charts_data = PythonOperator(
        task_id = "extract_charts",
        python_callable = get_all_chart_data,
        op_kwargs = {
            "token": CONFIG["SPOTIFY_TOKEN"],
            "start_date": datetime.strptime(CONFIG["EXTRACT_START_DATE"], "%Y-%m-%d"),
            "end_date": datetime.strptime(CONFIG["EXTRACT_END_DATE"], "%Y-%m-%d"),
            "csv_url": CONFIG["CSV_PATH"]
        }
    )

    upload_csv_to_s3 = PythonOperator(
        task_id = "upload_csv_to_s3",
        python_callable = upload_csv_s3,
        op_kwargs = {
            "files": [f"{table}.csv" for table in table_profiles.keys()],
            "csv_path": CONFIG["CSV_PATH"],
            "s3_bucket_name": CONFIG["AWS"]["S3_BUCKET_NAME"]
        }
    )

    create_redshift_tables = RedshiftDataOperator(
        task_id = "create_redshift_tables",
        database = CONFIG["AWS"]["REDSHIFT_DB"],
        sql = open(f"{CONFIG['SQL_PATH']}create_tables.sql").read(),
        cluster_identifier = CONFIG["AWS"]["REDSHIFT_CLUSTER_ID"],
        workgroup_name=None
    )

    with TaskGroup("transfer_s3_to_redshift") as transfer_s3_to_redshift:
        for table_name, profile in table_profiles.items():
            S3ToRedshiftOperator(
                task_id = f"transfer_{table_name}_s3_to_redshift",
                s3_bucket = CONFIG["AWS"]["S3_BUCKET_NAME"],
                s3_key = f"{table_name}.csv",
                schema = "PUBLIC",
                table = table_name,
                copy_options = profile["file_type"],
                method = "UPSERT",
                upsert_keys = profile["upsert_keys"]
            )

    dbt_transform = DbtTaskGroup(
        group_id = "dbt_transformations",
        project_config = ProjectConfig(CONFIG["DBT"]["DBT_PROJECT_PATH"]),
        profile_config = profile_config,
        execution_config = execution_config
    )

    setup_connections >> get_charts_data >> upload_csv_to_s3 >> create_redshift_tables >> transfer_s3_to_redshift >> dbt_transform


