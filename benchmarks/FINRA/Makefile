SHELL:=/bin/bash

HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops
FAASTLANE_PROJECT_HOME ?= $(HOME_DIR)/PycharmProjects/faastlane
FAASTLANE_WORK_DIR ?= $(CURDIR)/.faastlane

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest

################################################################################################################################################
################################################################################################################################################
# For Faastlane

Faastlane_ACTION_NAME = FINRA-Faastlane
MEGA_ACTION_NAME = megaFunction-FetchData4

BUILD_MODE ?= PURE_PYTHON_FILE
ifeq ("$(BUILD_MODE)","PURE_PYTHON_FILE")
	ACTION_ZIP = FINRA.zip
else
	ACTION_ZIP = FINRA-Virtualenv.zip
endif

__main__.py: marketdata.py lastpx.py side.py trddate.py volume.py marginBalance.py
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
	zip -r FINRA virtualenv requirements.txt data __main__.py marketdata.py lastpx.py side.py trddate.py volume.py marginBalance.py
.PHONY: pack-virtualenv-action
pack-virtualenv-action: FINRA-Virtualenv.zip

FINRA.zip: __main__.py data
	zip -r FINRA data __main__.py marketdata.py lastpx.py side.py trddate.py volume.py marginBalance.py
.PHONY: pack-action
pack-action: FINRA.zip

.action_is_newest: $(ACTION_ZIP)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(MEGA_ACTION_NAME) $(ACTION_ZIP) \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000 --main FetchData4
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(Faastlane_ACTION_NAME) $(ACTION_ZIP) \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .action_is_newest

action_invoke_Faastlane: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result $(Faastlane_ACTION_NAME) --param-file param.json --param op FT


################################################################################################################################################
################################################################################################################################################
# For OFC, Openwhisk, ChestBox

.marginBalance_action_is_deployed: marginBalance.py
	cp marginBalance.py __main__.py && zip -r marginBalance_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Three-marginBalance marginBalance_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .marginBalance_action_is_deployed

.lastpx_action_is_deployed: lastpx.py
	cp lastpx.py __main__.py && zip -r lastpx_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Three-lastpx lastpx_action.zip \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .lastpx_action_is_deployed

.volume_action_is_deployed: volume.py
	cp volume.py __main__.py && zip -r volume_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Three-volume volume_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .volume_action_is_deployed

.trddate_action_is_deployed: trddate.py
	cp trddate.py __main__.py && zip -r trddate_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Three-trddate trddate_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .trddate_action_is_deployed

.side_action_is_deployed: side.py
	cp side.py __main__.py && zip -r side_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Three-side side_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .side_action_is_deployed

.marketdata_action_is_deployed: marketdata.py
	cp marketdata.py __main__.py && zip -r marketdata_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Three-marketdata marketdata_action.zip \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .marketdata_action_is_deployed

.action_is_deployed: flowcontrol.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update FINRA-Three-flow flowcontrol.py \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .action_is_deployed

action_invoke_Openwhisk: .action_is_deployed .lastpx_action_is_deployed .side_action_is_deployed .marketdata_action_is_deployed .trddate_action_is_deployed .volume_action_is_deployed .marginBalance_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Three-flow --param-file param.json --param op OW

action_invoke_OFC: .action_is_deployed .lastpx_action_is_deployed .side_action_is_deployed .marketdata_action_is_deployed .trddate_action_is_deployed .volume_action_is_deployed .marginBalance_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Three-flow --param-file param.json --param op OFC

action_invoke_Faastorage: .action_is_deployed .lastpx_action_is_deployed .side_action_is_deployed .marketdata_action_is_deployed .trddate_action_is_deployed .volume_action_is_deployed .marginBalance_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result FINRA-Three-flow --param-file param.json --param op CB

clean:
	rm -rf .faastlane __main__.py
	rm -rf .action_is_newest .action_is_deployed .action_is_deployed .lastpx_action_is_deployed .side_action_is_deployed .marketdata_action_is_deployed .trddate_action_is_deployed .volume_action_is_deployed .marginBalance_action_is_deployed
	rm -rf FINRA.zip marketdata_action.zip lastpx_action.zip side_action.zip trddate_action.zip volume_action.zip marginBalance_action.zip
	# rm -rf result-*
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Three-flow
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Three-marketdata
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Three-trddate
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Three-volume
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Three-side
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Three-lastpx
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete FINRA-Three-marginBalance
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete $(Faastlane_ACTION_NAME)
	# sudo rm -rf virtualenv
