SHELL:=/bin/bash

HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest

ACTION_NAME = StateFunction

BUILD_MODE ?= PURE_PYTHON_FILE
ifeq ("$(BUILD_MODE)","PURE_PYTHON_FILE")
	ACTION_CODE = __main__.py
else
	ACTION_CODE = StateFunction-Virtualenv.zip
endif

.virtualenv_is_update: ipc-py-extend/ipc.cpp ipc-py-extend/ShareMemory.h ipc-py-extend/setup.py
	cd ipc-py-extend && python3.10 setup.py build
	docker run --rm -v ".:/StateFunction" --entrypoint bash $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) \
  -c "virtualenv -p 3.10 /StateFunction/virtualenv && \
  . /StateFunction/virtualenv/bin/activate  && \
  pip3 install /StateFunction/ipc-py-extend && \
  deactivate"
	touch .virtualenv_is_update

.PHONY: create-virtualenv
create-virtualenv: .virtualenv_is_update

StateFunction-Virtualenv.zip: __main__.py .virtualenv_is_update
	cp __main__.py __main__.py
	zip -r StateFunction-Virtualenv virtualenv __main__.py
	rm __main__.py

.PHONY: package-action
package-action: StateFunction-Virtualenv.zip

.action_is_newest: $(ACTION_CODE)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(ACTION_NAME)  $(ACTION_CODE) \
		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .action_is_newest

.PHONY: deploy-action
deploy-action: .action_is_newest

.PHONY: invoke-action-ping
invoke-action-ping: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result $(ACTION_NAME) --param op ping

.PHONY: invoke-action-create-shm
invoke-action-create-shm:.shm_is_create

.shm_is_create: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result $(ACTION_NAME) --param op create --param key 7777 --param size 40960
	touch .shm_is_create


.PHONY: invoke-action-destroy-shm
invoke-action-destroy-shm: .shm_is_create
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result $(ACTION_NAME) --param op destroy --param key 7777
	rm .shm_is_create

.PHONY: destroy-action
 destroy-action: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete $(ACTION_NAME)
	rm .action_is_newest

.PHONY: update-action
 update-action: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(ACTION_NAME) -m 1024


.PHONY: clear
clear:
	sudo rm -rf virtualenv
	rm -rf StateFunction-Virtualenv.zip .action_is_newest .virtualenv_is_update .shm_is_create
	rm -rf __main__.py
	rm -rf ipc-py-extend/build ipc-py-extend/ipc.egg-info
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete $(ACTION_NAME)
