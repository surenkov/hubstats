.PHONY: all
all: install-deps
all: build


.PHONY: activate
activate:
	. .env/bin/activate


.PHONY: install-deps
install-deps: activate
install-deps:
	- python3 -m pip install -r requirements.txt --target ./lib/vendor/
	@find ./lib/vendor -name '*.dist-info' -delete


.PHONY: build
build: activate
build:
	@mkdir ./build/
	python3 -m zipapp ./lib -p "/usr/bin/env python3" -o ./build/hubstats
	chmod +x ./build/hubstats

.PHONY: clean
clean:
	find ./lib/vendor -not -name '.gitkeep' -delete
	rm -rf ./build/
