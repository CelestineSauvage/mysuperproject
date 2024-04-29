
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
echo -e "AIRFLOW_GID=0" >> .env

sudo docker compose up airflow-init


cleanup 
    # Run docker compose down --volumes --remove-orphans command in the directory you downloaded the docker-compose.yaml file
    # Remove the entire directory where you downloaded the docker-compose.yaml file rm -rf '<DIRECTORY>'
    # Run through this guide from the very beginning, starting by re-downloading the docker-compose.yaml file


sudo docker compose up

# AIRFLOW_UID=1000
# AIRFLOW_GID=0
# The container is run as root user. For security, consider using a regular user account.
# ± % ls -ltr                                                                                                                                                                                              !1848
# total 28
# -rw-rw-r-- 1 lastrucci lastrucci 13005 avril 29 13:13 docker-compose.yaml
# drwxr-xr-x 2 lastrucci root       4096 avril 29 13:21 plugins
# drwxr-xr-x 2 lastrucci root       4096 avril 29 13:21 logs
# drwxr-xr-x 2 lastrucci root       4096 avril 29 13:21 dags

# AIRFLOW_UID=2000
# AIRFLOW_GID=0
# ls -ltr                                                                                                                                                                                              !1852
# total 28
# -rw-rw-r-- 1 lastrucci lastrucci 13005 avril 29 13:13 docker-compose.yaml
# drwxr-xr-x 2      2000 root       4096 avril 29 13:23 plugins
# drwxr-xr-x 2      2000 root       4096 avril 29 13:23 logs
# drwxr-xr-x 2      2000 root       4096 avril 29 13:23 dags




# sans env:
# ± % ls -ltr                                                                                                                                                                                              !1856
# total 28
# -rw-rw-r-- 1 lastrucci lastrucci 13005 avril 29 13:13 docker-compose.yaml
# drwxr-xr-x 2 root      root       4096 avril 29 13:24 plugins
# drwxr-xr-x 2 root      root       4096 avril 29 13:24 logs
# drwxr-xr-x 2 root      root       4096 avril 29 13:24 dags




# AIRFLOW_UID=50000
# AIRFLOW_GID=0
# airflow-init-1  | The container is run as root user. For security, consider using a regular user account.ls
# -rw-rw-r-- 1 lastrucci lastrucci 13005 avril 29 13:13 docker-compose.yaml
# drwxr-xr-x 2     50000 root       4096 avril 29 13:26 logs
# drwxr-xr-x 2     50000 root       4096 avril 29 13:26 dags
# drwxr-xr-x 2     50000 root       4096 avril 29 13:26 plugins

# my_task = DockerOperator(
#   task_id='my_task',
#   image='my_image',
#   container_name='my_task',
#   api_version='auto',
#   auto_remove=True,
#   docker_url='tcp://docker-proxy:2375',
#   network_mode='container:spark-master',
#   tty=True,
#   xcom_all=False,
#   mount_tmp_dir=False,
#   environment={
#   'SPARK_APPLICATION_ARGS': '{{ task_instance.xcom_pull(task_ids="store_prices") }}'
#         }
# params={"source_location": "/your/input_dir/path", "target_location": "/your/output_dir/path"},
# )

#     t2 = DockerOperator(
#         task_id='t2',
#         image='etl_extract:latest',
#         container_name='task_t2'
#         # command='' # sauf si tu as un entrypoint
#         docker_url='unix://var/run/docker.sock' # have to do : mount the socket on the container where ariflow instance is run
#         , network_mode='bridge' # separate my network containers to my network.
#         , auto_remove=True
#         , mounts=[
#             Mount(source='', target='', type='bind') #"source my machine"
#         ]
#         , mount_tmp_dir=False #when the container run inside an ther container
#     )


# from airflow.operators.python import ShortCircuitOperator
# t_is_data_available = ShortCircuitOperator(
#         task_id="check_if_data_available",
#         python_callable=lambda task_output: not task_output == "",
#         op_kwargs=dict(task_output=t_view.output),
#         dag=dag,
#     )