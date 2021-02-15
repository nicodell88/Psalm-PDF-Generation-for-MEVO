all: init run

init:
	pip install -r requirements.txt

run:
	python runPsalmAuto.py
	
.PHONY: init run