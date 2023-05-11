HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest


identifyphi/.identifyphi_action_is_deployed: identifyphi/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-Redis-identifyphi identifyphi/__main__.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch identifyphi/.identifyphi_action_is_deployed
.PHONY: identifyphi_action_invoke
identifyphi_action_invoke: identifyphi/.identifyphi_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-Redis-identifyphi --param-file identifyphi/param.json


anonymize/.anonymize_action_is_deployed: anonymize/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-Redis-anonymize anonymize/__main__.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch anonymize/.anonymize_action_is_deployed
.PHONY: anonymize_action_invoke
anonymize_action_invoke: anonymize/.anonymize_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-Redis-anonymize --param-file anonymize/param.json


analytics/.analytics_action_is_deployed: analytics/__main__.py
	cd analytics && zip -r analytics_action nltk_data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-Redis-analytics analytics/analytics_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch analytics/.analytics_action_is_deployed
.PHONY: analytics_action_invoke
analytics_action_invoke: analytics/.analytics_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-Redis-analytics --param-file analytics/param.json


.sequence_action_is_deployed: identifyphi/.identifyphi_action_is_deployed anonymize/.anonymize_action_is_deployed analytics/.analytics_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-Redis-sequence --sequence Healthcare-Analytics-Redis-identifyphi,Healthcare-Analytics-Redis-anonymize,Healthcare-Analytics-Redis-analytics
	touch .sequence_action_is_deployed

sequence_action_invoke: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-Redis-sequence --param-file identifyphi/param.json

clean:
	rm -rf .sequence_action_is_deployed identifyphi/.identifyphi_action_is_deployed anonymize/.anonymize_action_is_deployed analytics/.analytics_action_is_deployed
	rm -rf analytics/analytics_action.zip
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Redis-sequence
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Redis-analytics
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Redis-anonymize
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-Redis-identifyphi