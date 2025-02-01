

build:
	docker-compose -f airflow/docker-compose.yaml build

terraform_deploy:
	terraform -chdir=terraform/ init
	terraform -chdir=terraform/ apply

terraform_destroy:
	terraform -chdir=terraform/ destroy

aws_env:
	terraform -chdir=terraform/ output > airflow/aws.env

up:
	python airflow/get_spotify_token.py
	docker-compose -f airflow/docker-compose.yaml up -d

down:
	docker-compose -f airflow/docker-compose.yaml down
