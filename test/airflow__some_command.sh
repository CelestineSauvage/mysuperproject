
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
echo -e "AIRFLOW_GID=0" >> .env

sudo docker compose up airflow-init
sudo docker compose up -d


cleanup 
    # Run
    docker compose down --volumes --remove-orphans;
    mv .env ../test/airflow_env; mv docker-compose.yaml ../test/airflow_docker-compose.yaml ;
    sudo mv dags/docker_jobv2.py ../test/docker_jobv2.py; sudo mv dags/etl_dag.py ../test/etl_dag.py 
    cd ../; rm -rf airflow; mkdir airflow; cd airflow;
    mv ../test/airflow_env .env; mv ../test/airflow_docker-compose.yaml docker-compose.yaml

sudo docker compose up airflow-init
#
#sudo docker compose up -d
sudo mv ../test/docker_jobv2.py dags/docker_jobv2.py;
sudo mv  ../test/etl_dag.py dags/etl_dag.py
