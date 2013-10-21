# <variables>
CUSTOM_PIP_INDEX=localshop
export PYTHONPATH=`pwd`
export MYSQL_URI=mysql://root@localhost/instances
export REDIS_URI=redis://localhost:6379
export LOGLEVEL=DEBUG
# </variables>

all: test

prepare:
	@pip install -q curdling
	@curd install -r development.txt

clean:
	find . -name *.pyc -delete

test-kind:
	@-echo 'create database if not exists instances_test ' | mysql -uroot
	@TESTING=true INSTANCES_DB=mysql://root@localhost/instances_test INSTANCES_SETTINGS_MODULE="tests.settings" PYTHONPATH="$(PYTHONPATH)" \
		nosetests --with-coverage --cover-package=instances --nologcapture --logging-clear-handlers --stop --verbosity=2 -s tests/$(kind)

unit:
	@make test-kind kind=unit
functional:
	@make test-kind kind=functional

test: unit functional


shell:
	@PYTHONPATH=`pwd` ./instances/bin.py shell

release:
	@./.release
	@make publish


publish:
	@if [ -e "$$HOME/.pypirc" ]; then \
		echo "Uploading to '$(CUSTOM_PIP_INDEX)'"; \
		python setup.py register -r "$(CUSTOM_PIP_INDEX)"; \
		python setup.py sdist upload -r "$(CUSTOM_PIP_INDEX)"; \
	else \
		echo "You should create a file called \`.pypirc' under your home dir.\n"; \
		echo "That's the right place to configure \`pypi' repos.\n"; \
		echo "Read more about it here: https://github.com/Yipit/yipit/blob/dev/docs/rfc/RFC00007-python-packages.md"; \
		exit 1; \
	fi

run:
	@PYTHONPATH=`pwd` gunicorn -t 10000000000 -w 1 -b 127.0.0.1:5000 -k socketio.sgunicorn.GeventSocketIOWorker instances.server:app

check:
	@PYTHONPATH=`pwd` ./instances/bin.py check


local-migrate-forward:
	@[ "$(reset)" == "yes" ] && echo "drop database instances;create database instances" | mysql -uroot || echo "Running new migrations..."
	@alembic upgrade head

migrate-forward:
	echo "Running new migrations..."
	@alembic -c alembic.prod.ini upgrade head

local-migrate-back:
	@alembic downgrade -1

production-dump.sql:
	@printf "Getting production dump... "
	@mysqldump -u gbookmarks --password='b00k@BABY' -h mysql.gabrielfalcao.com instances_io_prod > production-dump.sql
	@echo "OK"
	@echo "Saved at production-dump.sql"

deploy:
	@fab -u root -H instanc.es deploy

create-machine:
	@fab -u root -H instanc.es create

full-deploy: create-machine deploy

sync:
	@git push
	@make deploy

redis-dump:
	@scp root@instanc.es:/var/lib/redis/*  /usr/local/var/db/redis/
