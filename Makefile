export PYTHONPATH=$(shell pwd)/
export PYTHONDONTWRITEBYTECODE=1


build: ## build docker-containers and apply alembic migrations
	docker-compose build

run: ## run the app container
	docker-compose run --service-ports -e --rm api bash -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" 

up: ## up all containers
	docker compose up -d

down: ## down all containers
	docker-compose down -v

bash: ## run and attach the app container
	docker-compose run --service-ports -e --rm api bash

unit_tests: ## run all tests without warnings
	docker compose run --service-ports -e --rm api bash -c "pytest ${test} --disable-warnings"

isort: # sort imports PEP8
	docker-compose run --service-ports -e --rm api bash -c "isort ."

black: # linter to organize readable code
	docker-compose run --service-ports -e --rm api bash -c "python -m black ."

host ?= http://localhost:8000
stress_tests:  ## Run stress tests ex: docker-compose run --service-ports -e --rm api bash -c "locust -f app/tests/stress_tests/locustfile.py --host http://127.0.0.1:8000"
	docker-compose run --service-ports -e --rm api bash -c "locust -f app/tests/stress_tests/locustfile.py --headless -u 1000 -r 17 --run-time 1m --host http://127.0.0.1:8000"