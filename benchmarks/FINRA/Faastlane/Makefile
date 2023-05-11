SHELL:=/bin/bash

HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops
FAASTLANE_PROJECT_HOME ?= $(HOME_DIR)/PycharmProjects/faastlane
FAASTLANE_WORK_DIR ?= $(CURDIR)/.faastlane

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest

ACTION_NAME = FINRA-Faastlane
MEGA_ACTION_NAME = megaFunction-FetchData4

BUILD_MODE ?= PURE_PYTHON_FILE
ifeq ("$(BUILD_MODE)","PURE_PYTHON_FILE")
	ACTION_ZIP = FINRA.zip
else
	ACTION_ZIP = FINRA-Virtualenv.zip
endif

__main__.py: marketdata.py lastpx.py side.py trddate.py volume.py marginBalance.py utils.py workflow.json
	FAASTLANE_WORK_DIR=$(FAASTLANE_WORK_DIR) python3 $(FAASTLANE_PROJECT_HOME)/composer/generator.py --input . --platform ow
	cp $(FAASTLANE_WORK_DIR)/__main__.py __main__.py
.PHONY: generate-faastlane-runner
generate-faastlane-runner: __main__.py

virtualenv: __main__.py data requirements.txt
	docker run --rm -v ".:/src" --entrypoint bash $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) \
      -c "mkdir /ttt /tt && cp -r /src/* /ttt && compile main /ttt /tt && mv /tt/virtualenv /src/ && exit"
.PHONY: create-virtualenv
create-virtualenv: virtualenv

FINRA-Virtualenv.zip:
	zip -r FINRA virtualenv requirements.txt data __main__.py marketdata.py lastpx.py side.py trddate.py volume.py marginBalance.py utils.py
.PHONY: pack-virtualenv-action
pack-virtualenv-action: FINRA-Virtualenv.zip

FINRA.zip: __main__.py data
	zip -r FINRA data __main__.py marketdata.py lastpx.py side.py trddate.py volume.py marginBalance.py utils.py
.PHONY: pack-action
pack-action: FINRA.zip

.action_is_newest: $(ACTION_ZIP)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(MEGA_ACTION_NAME) $(ACTION_ZIP) \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000 --main FetchData4
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(ACTION_NAME) $(ACTION_ZIP) \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .action_is_newest

.PHONY: update-action
update-action: .action_is_newest

.PHONY: invoke-action
invoke-action: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result $(ACTION_NAME) --param-file param.json

.PHONY: clear
clear:
	sudo rm -rf virtualenv
	rm -rf FINRA.zip
	rm -rf __main__.py .action_is_newest
	rm -rf .faastlane
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete $(ACTION_NAME)
