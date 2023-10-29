build:
	docker-compose --profile gpu build

run:
	docker-compose up -d

run-gpu:
	docker-compose --profile gpu up -d

stop:
	docker-compose down --remove-orphans

restart:
	docker-compose --profile gpu restart

kill-main:
	docker exec drone-detection_main_1 /app/src/stop

deploy-main: kill-main
	docker exec drone-detection_main_1 /app/src/run -q

kill-yolo-localization:
	docker exec drone-detection_yolo-localization_1 /app/src/stop

deploy-yolo-localization: kill-yolo-localization
	docker exec drone-detection_yolo-localization_1 /app/src/run -q

deploy: deploy-yolo-localization deploy-main

kill: kill-yolo-localization kill main