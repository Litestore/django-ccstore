# These targets are not files
.PHONY: install build_sandbox sandbox

install:
	pip3 install -r ../requirements-dev.txt

build_sandbox:
	python manage.py migrate
	python manage.py loaddata fixtures/cc_currency_dev.json
	python manage.py oscar_populate_countries --initial-only
	python manage.py clear_index --noinput
	python manage.py update_index catalogue
	python manage.py collectstatic --noinput

sandbox: install build_sandbox
