.PHONY: install doctor test start run backup stop

install:
	bash scripts/install.sh

doctor:
	bash scripts/doctor.sh

test:
	python3 -m pytest tests/ -q

start:
	bash scripts/start.sh

run:
	bash scripts/run-all.sh

backup:
	bash scripts/backup.sh

stop:
	bash scripts/stop.sh
