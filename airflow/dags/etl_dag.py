from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from docker.types import Mount


default_args = {
    'owner': 'airflow',
    'description': 'Use of the DockerOperator',
    'depend_on_past': False,
    'start_date': datetime(2021, 5, 1),
    'email_on_failure': False,
    'email_on_retry': False
}

source_main_volume = os.getenv("SOURCE_MAIN_VOLUME")
log_folder_name = os.getenv('LOG_FOLDER_NAME')
data_folder_name = os.getenv('DATA_FOLDER_NAME')

data_source = [{"FT": {
                "DOWNLOAD_FOLDER": f"{data_folder_name}/FT",
                "SOURCE": 0,
                "PUBLIEEDEPUIS": 1,
                # "ADDITIONAL_ARGUMENT": "--department 16",
                "FRANCE_EMPLOI_CLIENT_ID": os.getenv('FRANCE_EMPLOI_CLIENT_ID'),
                "FRANCE_EMPLOI_CLIENT_SECRET": os.getenv('FRANCE_EMPLOI_CLIENT_SECRET')
                }},
               {"APEC": {
                   "DOWNLOAD_FOLDER": f"{data_folder_name}/APEC",
                   "SOURCE": 1,
                   "PUBLIEEDEPUIS": "jour"
               }}
               ]

with DAG(
    'etl_dag_using_dockerOperator',
    default_args=default_args,
    schedule_interval="10 0 * * *",
    catchup=False,
    tags=['docker']
)as dag:

    start_dag = DummyOperator(
        task_id='start_dag'
    )

    end_dag = DummyOperator(
        task_id='end_dag'
    )

    for source in data_source:
        source_name, source_environement = list(source.items())[0]

        t_extract = DockerOperator(
            task_id=f'docker_extract_{source_name}',
            image='etl_extract:1.0.0',
            container_name=f'task___docker_extract_{source_name}',
            api_version='auto',
            auto_remove=True,
            docker_url='tcp://docker-proxy:2375',
            network_mode="airflow_airflow-jobmarket",
            mount_tmp_dir=False,
            mounts=[
                Mount(
                    source=f'{
                        source_main_volume}/{data_folder_name}/{source_name}',
                    target=f'/project/downloads_from_airflow/{source_name}',
                    type='bind'),
                Mount(source=f'{source_main_volume}/{log_folder_name}',
                      target='/project/logs', type='bind'),
            ],
            environment=source_environement
        )

        t_transform = DockerOperator(
            task_id=f'docker_transform_{source_name}',
            image='etl_transform:1.0.0',
            container_name=f'task___docker_transform_{source_name}',
            api_version='auto',
            auto_remove=True,
            docker_url='tcp://docker-proxy:2375',
            network_mode="airflow_airflow-jobmarket",
            mount_tmp_dir=False,
            mounts=[
                Mount(
                    source=f'{
                        source_main_volume}/{data_folder_name}/{source_name}',
                    target=f'/project/downloads_from_airflow/{source_name}',
                    type='bind'),
                Mount(source=f'{source_main_volume}/{log_folder_name}',
                      target='/project/logs',
                      type='bind'),
            ],
            environment=source_environement
        )

        t_load = DockerOperator(
            task_id=f'docker_load_{source_name}',
            image='etl_load_into_db:1.0.0',
            container_name=f'task___docker_load_{source_name}',
            api_version='auto',
            auto_remove=True,
            docker_url='tcp://docker-proxy:2375',
            network_mode="airflow_airflow-jobmarket",
            mount_tmp_dir=False,
            mounts=[
                Mount(
                    source=f'{
                        source_main_volume}/{data_folder_name}/{source_name}',
                    target=f'/project/downloads_from_airflow/{source_name}',
                    type='bind'),
                Mount(source=f'{source_main_volume}/{log_folder_name}',
                      target='/project/logs',
                      type='bind'),
            ],
            environment={
                "DOWNLOAD_FOLDER": f'{data_folder_name}/{source_name}',
                "MONGO_HOST": os.getenv('MONGO_HOST'),
                "MONGO_ADMIN": os.getenv('MONGO_ADMIN'),
                "MONGO_ADMIN_PASS": os.getenv('MONGO_ADMIN_PASS')
            }
        )
        start_dag >> t_extract >> t_transform >> t_load >> end_dag
