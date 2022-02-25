SHELL=bash
PORT?=4000
HOST?=0.0.0.0
CONDA_ENV = dnanalyzer
PDF_DIR=_pdf
PDF_HOST?=127.0.0.1
SITE_URL=http://${PDF_HOST}:${PORT}
PROTOCOLS=$(shell find _site/protocols/ -name 'index.html' | sed 's/_site\/protocols\///')

CONDA = $(shell which conda)
ifeq ($(CONDA),)
	CONDA=${HOME}/miniconda3/bin/conda
endif

CHROME=google-chrome-stable
ifeq ($(shell uname -s),Darwin)
	CHROME=/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome
endif

default: help

clean: ## cleanup the project
	@rm -rf _site
	@rm -rf .sass-cache
	@rm -rf .bundle
	@rm -rf vendor
.PHONY: clean

create-env: ## create conda environment
	if ${CONDA} env list | grep '^${CONDA_ENV}'; then \
	    ${CONDA} env update -f environment.yml; \
	else \
	    ${CONDA} env create -f environment.yml; \
	fi
.PHONY: create-env

ACTIVATE_ENV = source $(dir ${CONDA})activate ${CONDA_ENV}
install: clean ## install dependencies
	$(ACTIVATE_ENV) && \
		npm install && \
		gem install bundler && \
		bundle install
.PHONY: install

serve: ## run a local server
	$(ACTIVATE_ENV) && \
		bundle exec jekyll serve --strict_front_matter -d _site/DNAnalyzer -P ${PORT} -H ${PDF_HOST} ${FLAGS}
.PHONY: serve

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
