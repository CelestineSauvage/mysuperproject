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

with DAG('docker_operator_dag_V2', default_args=default_args, schedule_interval=None, catchup=False, tags=['docker']) as dag:
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
        
    t2 = DockerOperator(
        task_id='docker_extract_FT3',
        image='etl_extract:latest',
        container_name='task___command_sleep',
        api_version='auto',
        auto_remove=False,
        docker_url='tcp://docker-proxy:2375',
        network_mode="airflow_airflow-jobmarket",
        #the source should alreay be create
        mounts=[
            Mount(source='/home/lastrucci/Téléchargements/TEST_PROJECT/downloads_from_airflow/FT', target='/project/downloads_from_airflow/FT', type='bind'),
            Mount(source='/home/lastrucci/Téléchargements/TEST_PROJECT/logs_from_airflow', target='/project/logs', type='bind'),
            ],
        environment={
            "DOWNLOAD_FOLDER": "downloads_from_airflow/FT",
            "SOURCE": 0,
            "PUBLIEEDEPUIS": 1,
            "ADDITIONAL_ARGUMENT": "--department 13",
            "FRANCE_EMPLOI_CLIENT_ID": "PAR_jobmarketdatascientes_61aafad40553798b7d6198a1ece509eb5e20a3b1d239b478c3e09207209c9200",
            "FRANCE_EMPLOI_CLIENT_SECRET": "cdde83cbc9fb9d77ceb336af8d0dbacc1c11aaab3cd302f70792ab3c3a338e50"
            }
        )
    # docker_url="TCP://docker-socket-proxy:2375",
    # network_mode="airflow_airflow-jobmarket",
    # docker.errors.DockerException: Error while fetching server API version: 503 Server Error for http://docker-socket-proxy:2375/version: Service Unavailable ("<html><body><h1>503 Service Unavailable</h1>


    # host='docker-socket-y', port=2375
    # docker.errors.DockerException: Error while fetching server API version: HTTPConnectionPool(host='docker-socket-y', port=2375):
    # Max retries exceeded with url: /version (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7654f538d400>:
    #  Failed to establish a new connection: [Errno -3] Temporary failure in name resolution'))

    t3 = DockerOperator(
        task_id='docker_command_hello',
        image='docker_image_task',
        container_name='task___command_hello',
        api_version='auto',
        auto_remove=True,
        command="/bin/sleep 40",
        docker_url="unix://var/run/docker.sock",
        network_mode="airflow_airflow-jobmarket"
        )

    t4 = BashOperator(
        task_id='print_hello',
        bash_command='echo "hello world"'
        )

    start_dag >> t1 
    
    t1 >> t2 >> t4
    t1 >> t3 >> t4

    t4 >> end_dag