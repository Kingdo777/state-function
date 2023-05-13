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

ACTION_NAME = Healthcare-Analytics-Faastlane

BUILD_MODE ?= PURE_PYTHON_FILE
ifeq ("$(BUILD_MODE)","PURE_PYTHON_FILE")
	ACTION_ZIP = Healthcare-Analytics.zip
else
	ACTION_ZIP = Healthcare-Analytics-Virtualenv.zip
endif

__main__.py: anonymize.py analytics.py identifyphi.py workflow.json
	FAASTLANE_WORK_DIR=$(FAASTLANE_WORK_DIR) python3 $(FAASTLANE_PROJECT_HOME)/composer/generator.py --input . --platform ow
	cp $(FAASTLANE_WORK_DIR)/__main__.py __main__.py
.PHONY: generate-faastlane-runner
generate-faastlane-runner: __main__.py

virtualenv: __main__.py nltk_data requirements.txt
	docker run --rm -v ".:/src" --entrypoint bash $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) \
      -c "mkdir /ttt /tt && cp -r /src/* /ttt && compile main /ttt /tt && mv /tt/virtualenv /src/ && exit"
.PHONY: create-virtualenv
create-virtualenv: virtualenv

Healthcare-Analytics-Virtualenv.zip:
	zip -r Healthcare-Analytics virtualenv requirements.txt nltk_data __main__.py identifyphi.py anonymize.py analytics.py
.PHONY: pack-virtualenv-action
pack-virtualenv-action: Healthcare-Analytics-Virtualenv.zip

Healthcare-Analytics.zip: __main__.py nltk_data
	zip -r Healthcare-Analytics nltk_data __main__.py identifyphi.py anonymize.py analytics.py
.PHONY: pack-action
pack-action: Healthcare-Analytics.zip

.action_is_newest: $(ACTION_ZIP)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(ACTION_NAME) $(ACTION_ZIP) \
		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .action_is_newest

action_invoke_Faastlane: .action_is_newest
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-Faastlane --param-file param.json --param op FT

################################################################################################################################################
################################################################################################################################################
# For OFC, Openwhisk, ChestBox

.identifyphi_action_is_deployed: identifyphi.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-Three-identifyphi identifyphi.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .identifyphi_action_is_deployed

.anonymize_action_is_deployed: anonymize.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-Three-anonymize anonymize.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .anonymize_action_is_deployed

.analytics_action_is_deployed: analytics.py
	cp analytics.py __main__.py && zip -r analytics_action nltk_data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-Three-analytics analytics_action.zip \
  --docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .analytics_action_is_deployed

.sequence_action_is_deployed: .identifyphi_action_is_deployed .anonymize_action_is_deployed .analytics_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-Three-sequence --sequence Healthcare-Analytics-Three-identifyphi,Healthcare-Analytics-Three-anonymize,Healthcare-Analytics-Three-analytics
	touch .sequence_action_is_deployed

action_invoke_OFC: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-Three-sequence --param-file param.json --param op OFC

action_invoke_Faastorage: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-Three-sequence --param-file param.json --param op CB

action_invoke_Openwhisk: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-Three-sequence --param-file param.json --param op OW

clean:
	rm -rf .sequence_action_is_deployed .identifyphi_action_is_deployed .anonymize_action_is_deployed .analytics_action_is_deployed __main__.py .action_is_newest
	rm -rf result-*
	rm -rf analytics_action.zip Healthcare-Analytics.zip
	rm -rf .faastlane
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Faastlane
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Three-sequence
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Three-analytics
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Three-anonymize
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Three-identifyphi
	#sudo rm -rf virtualenv