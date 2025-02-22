FROM apache/airflow:2.7.1-python3.11

ENV AIRFLOW_HOME=/opt/airflow/

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

USER airflow

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    PIP_USER= pip install --no-cache-dir dbt-redshift && deactivate


WORKDIR $AIRFLOW_HOME
