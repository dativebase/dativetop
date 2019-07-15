.DEFAULT_GOAL := help

THIS_FILE := $(lastword $(MAKEFILE_LIST))

build-wheel:  ## Build the Wheel (.whl) file under dist/
	python setup.py sdist bdist_wheel

help:  ## Print this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
