from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from docker.types import Mount


default_args = {
'owner'                 : 'airflow',
'description'           : 'Use of the DockerOperator',
'depend_on_past'        : False,
'start_date'            : datetime(2021, 5, 1),
'email_on_failure'      : False,
'email_on_retry'        : False
# 'retries'               : 1,
# 'retry_delay'           : timedelta(minutes=5)
}

data_source = [{"FT": {
                "DOWNLOAD_FOLDER": f"downloads_from_airflow/FT",
                "SOURCE": 0,
                "PUBLIEEDEPUIS": 1,
                "ADDITIONAL_ARGUMENT": "--department 13",
                "FRANCE_EMPLOI_CLIENT_ID": "PAR_jobmarketdatascientes_61aafad40553798b7d6198a1ece509eb5e20a3b1d239b478c3e09207209c9200",
                "FRANCE_EMPLOI_CLIENT_SECRET": "cdde83cbc9fb9d77ceb336af8d0dbacc1c11aaab3cd302f70792ab3c3a338e50"
                }},
                {"APEC": {
                "DOWNLOAD_FOLDER": f"downloads_from_airflow/APEC",
                "SOURCE": 1,
                "PUBLIEEDEPUIS": "jour"
                }}
                ]

source_log_volume = "/home/lastrucci/Téléchargements/TEST_PROJECT/logs_from_airflow"
source_data_volume = "/home/lastrucci/Téléchargements/TEST_PROJECT/downloads_from_airflow/"

with DAG(
    'docker_operator_dag_V2',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=['docker']
)as dag:

    start_dag = DummyOperator(
        task_id='start_dag'
        )

    end_dag = DummyOperator(
        task_id='end_dag'
        )        

    t1 = BashOperator(
        task_id='print_current_date2',
        bash_command='date'
        )
    
    t5 = BashOperator(
        task_id='print_hello',
        bash_command='echo "hello world"'
        )

    for source in data_source:
        source_name, source_environement = list(source.items())[0]

        
        t2 = DockerOperator(
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
                    source=f'{source_data_volume}/{source_name}',
                    target=f'/project/downloads_from_airflow/{source_name}',
                    type='bind'),
                Mount(source=source_log_volume, target='/project/logs', type='bind'),
                ],
            environment=source_environement
            )

        t3 = DockerOperator(
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
                    source=f'{source_data_volume}/{source_name}',
                    target=f'/project/downloads_from_airflow/{source_name}',
                    type='bind'),
                Mount(source=source_log_volume,  target='/project/logs', type='bind'),
                ],
            environment=source_environement
            )

        t4 = DockerOperator(
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
                    source=f'{source_data_volume}/{source_name}',
                    target=f'/project/downloads_from_airflow/{source_name}',
                    type='bind'),
                Mount(source=source_log_volume,  target='/project/logs', type='bind'),
                ],
            environment={
                "DOWNLOAD_FOLDER": f"downloads_from_airflow/{source_name}",
                "MONGO_HOST": "my_mongo",
                "MONGO_ADMIN": "admin",
                "MONGO_ADMIN_PASS": "pass"
            }
            )
        start_dag >> t1 >> t2 >> t3 >> t4 >> t5 >> end_dag
