build:
	docker-compose -f airflow/docker-compose.yaml build

terraform_deploy:
	terraform -chdir=terraform/ init
	terraform -chdir=terraform/ apply
	terraform -chdir=terraform/ output > airflow/dags/config/aws_config.env
	@sed -i "s|redshift_password = <sensitive>|redshift_password = $$(terraform -chdir=terraform/ output redshift_password)|" airflow/dags/config/aws_config.env	

terraform_destroy:
	terraform -chdir=terraform/ destroy

up:
	python airflow/scripts/get_spotify_token.py
	docker-compose -f airflow/docker-compose.yaml up -d

down:
	docker-compose -f airflow/docker-compose.yaml down
