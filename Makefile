.PHONY: test eval demo
test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
eval:
	PYTHONPATH=src python3 evals/run.py
demo:
	PYTHONPATH=src python3 -m voice_gateway.demo

