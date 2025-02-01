import os
import datetime as dt

from dotenv import load_dotenv 
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from extract_data import get_all_chart_data
from upload_to_s3 import upload_csv_s3

load_dotenv()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1
}

# constants
EXT_START_DATE = dt.datetime(2024, 1, 1)
EXT_END_DATE = dt.datetime(2024, 1, 5)
SPOTIFY_TOKEN = os.getenv('SPOTIFY_ACCESS_TOKEN')
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
CSV_PATH = f'{AIRFLOW_HOME}data/'

with DAG(
    dag_id=f'load_charts_dag',
    default_args=default_args,
    description=f"Load and upload charts data to S3",
    schedule_interval="@daily",
    catchup=False,
    tags=['spotify']
) as dag:
    get_charts_data = PythonOperator(
        task_id = "extract_spotify_charts",
        python_callable = get_all_chart_data,
        op_kwargs = {
            'token': SPOTIFY_TOKEN,
            'start_date': EXT_START_DATE,
            'end_date': EXT_END_DATE,
            'csv_url': CSV_PATH
        }        
    )

    upload_csv_to_s3 = PythonOperator(
        task_id = "upload_csv_to_s3",
        python_callable = upload_csv_s3,
        op_kwargs = {
            'files': ['artists.csv', 'chart_data.csv', 'track_artists.csv', 'tracks.csv']
        }
    )

    get_charts_data >> upload_csv_to_s3