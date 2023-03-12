SHELL:=/bin/bash

HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops
FAASTLANE_PROJECT_HOME ?= $(HOME_DIR)/PycharmProjects/faastlane

DOCKER_IMAGE = kingdo/action-python-v2.7
DOCKER_IMAGE_TAG = latest

ACTION_NAME = ML-Prediction-Faastlane

BUILD_MODE ?= PURE_PYTHON_FILE
ifeq ("$(BUILD_MODE)","PURE_PYTHON_FILE")
	ACTION_ZIP = ML-Prediction.zip
else
	ACTION_ZIP = ML-Prediction-Virtualenv.zip
endif

__main__.py: predict.py render.py resize.py utils.py workflow.json
	python3 $(FAASTLANE_PROJECT_HOME)/composer/generator.py --input . --platform ow
	cp .faastlane/__main__.py __main__.py
.PHONY: generate-faastlane-runner
generate-faastlane-runner: __main__.py

virtualenv: __main__.py data requirements.txt
	docker run --rm -v ".:/src" --entrypoint bash $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) \
      -c "mkdir /ttt /tt && cp -r /src/* /ttt && compile main /ttt /tt && mv /tt/virtualenv /src/ && exit"
.PHONY: create-virtualenv
create-virtualenv: virtualenv

ML-Prediction-Virtualenv.zip:
	zip -r ML-Prediction virtualenv requirements.txt data __main__.py resize.py predict.py render.py utils.py
.PHONY: pack-virtualenv-action
pack-virtualenv-action: ML-Prediction-Virtualenv.zip

ML-Prediction.zip: __main__.py data
	zip -r ML-Prediction data __main__.py resize.py predict.py render.py utils.py
.PHONY: pack-action
pack-action: ML-Prediction.zip

.action_is_newest: $(ACTION_ZIP)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(ACTION_NAME) $(ACTION_ZIP) \
		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .action_is_newest

.PHONY: update-action
update-action: .action_is_newest

.PHONY: invoke-action
invoke-action: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result $(ACTION_NAME) --param name World

.PHONY: clear
clear:
	sudo rm -rf virtualenv
	rm -rf ML-Prediction.zip
	rm -rf __main__.py
	rm -rf .faastlane
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete $(ACTION_NAME)
