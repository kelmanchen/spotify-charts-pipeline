from airflow import settings
from airflow.models import Connection

def create_airflow_connections(access_key, secret_key, region, redshift_user, redshift_password, redshift_db, redshift_host, redshift_port):
    session = settings.Session()
    
    # AWS Connection
    aws_conn = Connection(
        conn_id="aws_default",
        conn_type="aws",
        login=access_key,
        password=secret_key,
        extra={
            "region_name": region
        }
    )

    # Redshift Connection
    redshift_conn = Connection(
        conn_id="redshift_default",
        conn_type="postgres",
        host=redshift_host,
        login=redshift_user,
        password=redshift_password,
        port=redshift_port,
        schema=redshift_db
    )

    session.add(aws_conn)
    session.add(redshift_conn)
    session.commit()
