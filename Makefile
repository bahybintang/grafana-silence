init-workspace:
	mkdir log
	python3 -m venv venv
	. venv/bin/activate

install:
	python3 -m pip install -r requirements.txt

run:
	python3 main.py

build:
	docker build -t bintangbahy/grafana-silence:latest .