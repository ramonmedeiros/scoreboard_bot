
default: test

test:
	python -m pytest -s

run: 
	eval "$(shell cat Procfile | grep -E "gunicorn.*" -o)"

lint:
	yapf -i -r scoreboard
	yapf -i -r tests
