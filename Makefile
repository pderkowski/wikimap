.PHONY: test

test:
	python -m unittest discover -s src/ -v
