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
		gem install bundler && \
		bundle install
.PHONY: install

serve: ## run a local server
	$(ACTIVATE_ENV) && \
		bundle exec jekyll serve
.PHONY: serve

detached-serve: ## run a local server in detached mode
	$(ACTIVATE_ENV) && \
		bundle exec jekyll serve --detach -P ${PORT} -H ${PDF_HOST} ${FLAGS}
.PHONY: detached-serve

pdf: detached-serve ## generate the PDF of the protocols
	mkdir -p $(PDF_DIR)
	@for t in $(PROTOCOLS); do \
		name="$(PDF_DIR)/$$(echo $$t | tr '/' '-' | sed -e 's/.html/-instructors.pdf/' -e 's/^-//' -e 's/-index//')"; \
		${CHROME} \
            --headless \
            --disable-gpu \
            --print-to-pdf="$$name" \
            "$(SITE_URL)/protocols/$$t" \
            2> /dev/null ; \
		name="$(PDF_DIR)/$$(echo $$t | tr '/' '-' | sed -e 's/.html/-learners.pdf/' -e 's/^-//' -e 's/-index//')"; \
		${CHROME} \
            --headless \
            --disable-gpu \
            --print-to-pdf="$$name" \
            "$(SITE_URL)/protocols/$$t?without-details" \
            2> /dev/null ; \
	done

	${CHROME} \
		--headless \
		--disable-gpu \
		--print-to-pdf="$(PDF_DIR)/beer-dna-sequencing-flongle-instructor.pdf" \
		"$(SITE_URL)/protocols/beer-dna-sequencing?flongle" \
		2> /dev/null

	${CHROME} \
		--headless \
		--disable-gpu \
		--print-to-pdf="$(PDF_DIR)/beer-dna-sequencing-flongle-learners.pdf" \
		"$(SITE_URL)/protocols/beer-dna-sequencing?flongle?without-details" \
		2> /dev/null
	

	pkill -f jekyll
.PHONY: pdf

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
