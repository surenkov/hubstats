.PHONY: all
all: install-deps
all: build-zipapp


.PHONY: activate
activate:
	. .env/bin/activate


.PHONY: install-deps
install-deps: activate
install-deps:
	python3 -m pip install -r requirements.txt --target ./vendor/


.PHONY: build-zipapp
build-app: activate
build-zipapp:
	python3 -m zipapp -p "/usr/bin/env python3" -m "hubstats:main" -o ./build/hubstats
	chmod +x ./build/hubstats
