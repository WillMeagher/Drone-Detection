build:
	docker-compose --profile gpu

run:
	docker-compose up -d

run-gpu:
	docker-compose --profile gpu up -d

stop:
	docker-compose down --remove-orphans

restart:
	docker-compose --profile gpu restart